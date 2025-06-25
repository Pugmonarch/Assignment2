# parser.py - Enhanced to support both Horn clauses and general propositional logic

import re
from knowledge_base import KnowledgeBase, Rule, LogicalExpression, Atom, Negation, Conjunction, Disjunction, Implication, Biconditional, GeneralKnowledgeBase

def parse_file(filename):
    """Parse file - automatically detects Horn vs General logic"""
    # First, check if it's a general logic file
    if is_general_logic_file(filename):
        return parse_general_file(filename)
    else:
        return parse_horn_file(filename)

def is_general_logic_file(filename):
    """Check if file contains general propositional logic operators"""
    try:
        with open(filename, 'r') as file:
            content = file.read()
            # Look for general logic operators
            return any(op in content for op in ['||', '<=>', '~'])
    except:
        return False

def parse_horn_file(filename):
    """Original Horn clause parser"""
    with open(filename, 'r') as file:
        lines = file.readlines()

    kb = KnowledgeBase()
    query = None
    mode = None

    for line in lines:
        line = line.strip()

        if not line:
            continue  # skip empty lines

        if line == "TELL":
            mode = "TELL"
            continue
        elif line == "ASK":
            mode = "ASK"
            continue

        if mode == "TELL":
            parse_horn_tell_line(line, kb)
        elif mode == "ASK":
            query = line.strip()

    return kb, query

def parse_horn_tell_line(line, kb):
    """Parse Horn clause line"""
    if '=>' in line:
        premises_str, conclusion = line.split('=>')
        conclusion = conclusion.strip()
        premises = [p.strip() for p in premises_str.split('&')]
        rule = Rule(premises, conclusion)
        kb.add_rule(rule)
    else:
        # It's a fact
        fact = line.strip()
        kb.add_fact(fact)

# General Logic Parser Components

def tokenize(expression):
    """Tokenize a logical expression"""
    token_patterns = [
        (r'\s+', None),  # Skip whitespace
        (r'<=>', 'BICONDITIONAL'),
        (r'=>', 'IMPLICATION'), 
        (r'\|\|', 'DISJUNCTION'),
        (r'&', 'CONJUNCTION'),
        (r'~', 'NEGATION'),
        (r'\(', 'LPAREN'),
        (r'\)', 'RPAREN'),
        (r'[a-z][0-9]*', 'ATOM'),  # Variables like p, p1, p2, etc.
    ]
    
    tokens = []
    i = 0
    while i < len(expression):
        for pattern, token_type in token_patterns:
            regex = re.compile(pattern)
            match = regex.match(expression, i)
            if match:
                if token_type:  # Skip whitespace (None type)
                    tokens.append((token_type, match.group()))
                i = match.end()
                break
        else:
            raise ValueError(f"Invalid character at position {i}: {expression[i]}")
    
    return tokens

class ExpressionParser:
    """Recursive descent parser for logical expressions"""
    
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
    
    def peek(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None
    
    def consume(self, expected_type=None):
        if self.pos < len(self.tokens):
            token = self.tokens[self.pos]
            self.pos += 1
            if expected_type and token[0] != expected_type:
                raise ValueError(f"Expected {expected_type}, got {token[0]}")
            return token
        raise ValueError("Unexpected end of expression")
    
    def parse(self):
        """Parse the entire expression"""
        expr = self.parse_biconditional()
        if self.pos < len(self.tokens):
            raise ValueError(f"Unexpected token: {self.tokens[self.pos]}")
        return expr
    
    def parse_biconditional(self):
        """Parse biconditional expressions (lowest precedence)"""
        left = self.parse_implication()
        
        while self.peek() and self.peek()[0] == 'BICONDITIONAL':
            self.consume('BICONDITIONAL')
            right = self.parse_implication()
            left = Biconditional(left, right)
        
        return left
    
    def parse_implication(self):
        """Parse implication expressions"""
        left = self.parse_disjunction()
        
        while self.peek() and self.peek()[0] == 'IMPLICATION':
            self.consume('IMPLICATION')
            right = self.parse_disjunction()
            left = Implication(left, right)
        
        return left
    
    def parse_disjunction(self):
        """Parse disjunction (OR) expressions"""
        left = self.parse_conjunction()
        
        while self.peek() and self.peek()[0] == 'DISJUNCTION':
            self.consume('DISJUNCTION')
            right = self.parse_conjunction()
            left = Disjunction(left, right)
        
        return left
    
    def parse_conjunction(self):
        """Parse conjunction (AND) expressions"""
        left = self.parse_negation()
        
        while self.peek() and self.peek()[0] == 'CONJUNCTION':
            self.consume('CONJUNCTION')
            right = self.parse_negation()
            left = Conjunction(left, right)
        
        return left
    
    def parse_negation(self):
        """Parse negation expressions"""
        if self.peek() and self.peek()[0] == 'NEGATION':
            self.consume('NEGATION')
            operand = self.parse_negation()  # Allow multiple negations
            return Negation(operand)
        
        return self.parse_primary()
    
    def parse_primary(self):
        """Parse primary expressions (atoms and parenthesized expressions)"""
        token = self.peek()
        
        if not token:
            raise ValueError("Unexpected end of expression")
        
        if token[0] == 'ATOM':
            self.consume('ATOM')
            return Atom(token[1])
        elif token[0] == 'LPAREN':
            self.consume('LPAREN')
            expr = self.parse_biconditional()
            self.consume('RPAREN')
            return expr
        else:
            raise ValueError(f"Unexpected token: {token}")

def parse_general_file(filename):
    """Parse a file with general propositional logic"""
    with open(filename, 'r') as file:
        lines = file.readlines()
    
    kb = GeneralKnowledgeBase()
    query = None
    mode = None
    
    for line in lines:
        line = line.strip()
        
        if not line:
            continue
        
        if line == "TELL":
            mode = "TELL"
            continue
        elif line == "ASK":
            mode = "ASK"
            continue
        
        if mode == "TELL":
            # Parse each sentence as a general logical expression
            tokens = tokenize(line)
            parser = ExpressionParser(tokens)
            sentence = parser.parse()
            kb.add_sentence(sentence)
        elif mode == "ASK":
            # Query should be a simple atom for now
            query = line.strip()
    
    return kb, query

def extract_atoms(expr):
    """Extract all atomic propositions from a logical expression"""
    atoms = set()
    
    if isinstance(expr, Atom):
        atoms.add(expr.symbol)
    elif isinstance(expr, Negation):
        atoms.update(extract_atoms(expr.operand))
    elif hasattr(expr, 'left') and hasattr(expr, 'right'):  # Binary expressions
        atoms.update(extract_atoms(expr.left))
        atoms.update(extract_atoms(expr.right))
    
    return atoms