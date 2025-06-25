# knowledge_base.py - Enhanced to support both Horn clauses and general propositional logic

class Rule:
    """
    Represents a Horn clause rule.
    Example: a & b => c
    """
    def __init__(self, premises, conclusion):
        self.premises = premises  # list of symbols
        self.conclusion = conclusion  # single symbol

class KnowledgeBase:
    """
    Stores facts and rules parsed from Horn clause TELL section.
    """
    def __init__(self):
        self.facts = set()  # known true propositions
        self.rules = []     # list of Rule objects

    def add_fact(self, fact):
        self.facts.add(fact)

    def add_rule(self, rule):
        self.rules.append(rule)

# General Propositional Logic Classes

class LogicalExpression:
    """Base class for logical expressions"""
    pass

class Atom(LogicalExpression):
    """Atomic proposition (single symbol)"""
    def __init__(self, symbol):
        self.symbol = symbol
    
    def __str__(self):
        return self.symbol
    
    def __eq__(self, other):
        return isinstance(other, Atom) and self.symbol == other.symbol
    
    def __hash__(self):
        return hash(self.symbol)

class Negation(LogicalExpression):
    """Negation (~p)"""
    def __init__(self, operand):
        self.operand = operand
    
    def __str__(self):
        return f"~{self.operand}"
    
    def __eq__(self, other):
        return isinstance(other, Negation) and self.operand == other.operand
    
    def __hash__(self):
        return hash(('~', self.operand))

class BinaryExpression(LogicalExpression):
    """Base for binary logical expressions"""
    def __init__(self, left, right, operator):
        self.left = left
        self.right = right
        self.operator = operator
    
    def __str__(self):
        return f"({self.left} {self.operator} {self.right})"
    
    def __eq__(self, other):
        return (isinstance(other, type(self)) and 
                self.left == other.left and 
                self.right == other.right)
    
    def __hash__(self):
        return hash((self.operator, self.left, self.right))

class Conjunction(BinaryExpression):
    """AND operation (p & q)"""
    def __init__(self, left, right):
        super().__init__(left, right, "&")

class Disjunction(BinaryExpression):
    """OR operation (p || q)"""
    def __init__(self, left, right):
        super().__init__(left, right, "||")

class Implication(BinaryExpression):
    """Implication (p => q)"""
    def __init__(self, left, right):
        super().__init__(left, right, "=>")

class Biconditional(BinaryExpression):
    """Biconditional (p <=> q)"""
    def __init__(self, left, right):
        super().__init__(left, right, "<=>")

class GeneralKnowledgeBase:
    """Extended knowledge base for general propositional logic"""
    def __init__(self):
        self.sentences = []  # List of LogicalExpression objects
    
    def add_sentence(self, sentence):
        self.sentences.append(sentence)
    
    def __str__(self):
        return "\n".join(str(sentence) for sentence in self.sentences)

# Resolution-specific classes

class Clause:
    """Represents a clause (disjunction of literals) for resolution"""
    def __init__(self, literals):
        # literals is a set of strings, where negative literals start with '~'
        self.literals = set(literals) if literals else set()
    
    def __str__(self):
        if not self.literals:
            return "□"  # Empty clause (contradiction)
        return " || ".join(sorted(self.literals))
    
    def __eq__(self, other):
        return isinstance(other, Clause) and self.literals == other.literals
    
    def __hash__(self):
        return hash(frozenset(self.literals))
    
    def is_empty(self):
        return len(self.literals) == 0
    
    def is_unit(self):
        """Check if this is a unit clause (single literal)"""
        return len(self.literals) == 1
    
    def get_unit_literal(self):
        """Get the single literal from a unit clause"""
        if self.is_unit():
            return next(iter(self.literals))
        return None