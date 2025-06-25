# resolution_prover.py
# Resolution-based theorem prover for general propositional logic

from parser import *

class Clause:
    """Represents a clause (disjunction of literals)"""
    def __init__(self, literals):
        # literals is a set of strings, where negative literals start with '~'
        self.literals = set(literals)
    
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

def negate_literal(literal):
    """Negate a literal"""
    if literal.startswith('~'):
        return literal[1:]  # Remove negation
    else:
        return '~' + literal  # Add negation

def convert_to_cnf(expr):
    """Convert a logical expression to Conjunctive Normal Form (CNF)"""
    # This is a simplified CNF conversion
    # For a complete implementation, you'd need more sophisticated algorithms
    
    def eliminate_biconditionals(expr):
        """Replace p <=> q with (p => q) & (q => p)"""
        if isinstance(expr, Biconditional):
            left_to_right = Implication(expr.left, expr.right)
            right_to_left = Implication(expr.right, expr.left)
            return Conjunction(left_to_right, right_to_left)
        elif isinstance(expr, BinaryExpression):
            return type(expr)(eliminate_biconditionals(expr.left), 
                            eliminate_biconditionals(expr.right))
        elif isinstance(expr, Negation):
            return Negation(eliminate_biconditionals(expr.operand))
        else:
            return expr
    
    def eliminate_implications(expr):
        """Replace p => q with ~p || q"""
        if isinstance(expr, Implication):
            return Disjunction(Negation(expr.left), expr.right)
        elif isinstance(expr, BinaryExpression):
            return type(expr)(eliminate_implications(expr.left), 
                            eliminate_implications(expr.right))
        elif isinstance(expr, Negation):
            return Negation(eliminate_implications(expr.operand))
        else:
            return expr
    
    def move_negations_inward(expr):
        """Apply De Morgan's laws"""
        if isinstance(expr, Negation):
            if isinstance(expr.operand, Negation):
                # Double negation elimination
                return move_negations_inward(expr.operand.operand)
            elif isinstance(expr.operand, Conjunction):
                # ~(p & q) becomes ~p || ~q
                left = move_negations_inward(Negation(expr.operand.left))
                right = move_negations_inward(Negation(expr.operand.right))
                return Disjunction(left, right)
            elif isinstance(expr.operand, Disjunction):
                # ~(p || q) becomes ~p & ~q
                left = move_negations_inward(Negation(expr.operand.left))
                right = move_negations_inward(Negation(expr.operand.right))
                return Conjunction(left, right)
            else:
                return expr
        elif isinstance(expr, BinaryExpression):
            return type(expr)(move_negations_inward(expr.left), 
                            move_negations_inward(expr.right))
        else:
            return expr
    
    def distribute_or_over_and(expr):
        """Distribute OR over AND to get CNF"""
        if isinstance(expr, Disjunction):
            left = distribute_or_over_and(expr.left)
            right = distribute_or_over_and(expr.right)
            
            if isinstance(left, Conjunction):
                # (A & B) || C becomes (A || C) & (B || C)
                a_or_right = distribute_or_over_and(Disjunction(left.left, right))
                b_or_right = distribute_or_over_and(Disjunction(left.right, right))
                return Conjunction(a_or_right, b_or_right)
            elif isinstance(right, Conjunction):
                # A || (B & C) becomes (A || B) & (A || C)
                left_or_b = distribute_or_over_and(Disjunction(left, right.left))
                left_or_c = distribute_or_over_and(Disjunction(left, right.right))
                return Conjunction(left_or_b, left_or_c)
            else:
                return Disjunction(left, right)
        elif isinstance(expr, Conjunction):
            return Conjunction(distribute_or_over_and(expr.left), 
                             distribute_or_over_and(expr.right))
        elif isinstance(expr, Negation):
            return Negation(distribute_or_over_and(expr.operand))
        else:
            return expr
    
    # Apply transformations step by step
    expr = eliminate_biconditionals(expr)
    expr = eliminate_implications(expr)
    expr = move_negations_inward(expr)
    expr = distribute_or_over_and(expr)
    
    return expr

def extract_clauses_from_cnf(cnf_expr):
    """Extract clauses from CNF expression"""
    clauses = []
    
    def extract_from_conjunction(expr):
        if isinstance(expr, Conjunction):
            extract_from_conjunction(expr.left)
            extract_from_conjunction(expr.right)
        else:
            # This should be a disjunction or a single literal
            literals = extract_literals_from_disjunction(expr)
            clauses.append(Clause(literals))
    
    def extract_literals_from_disjunction(expr):
        literals = set()
        
        def collect_literals(e):
            if isinstance(e, Disjunction):
                collect_literals(e.left)
                collect_literals(e.right)
            elif isinstance(e, Negation) and isinstance(e.operand, Atom):
                literals.add('~' + e.operand.symbol)
            elif isinstance(e, Atom):
                literals.add(e.symbol)
            else:
                # For more complex cases, you might need additional handling
                pass
        
        collect_literals(expr)
        return literals
    
    extract_from_conjunction(cnf_expr)
    return clauses

def resolve(clause1, clause2):
    """Attempt to resolve two clauses"""
    resolvents = []
    
    # Find complementary literals
    for lit1 in clause1.literals:
        neg_lit1 = negate_literal(lit1)
        if neg_lit1 in clause2.literals:
            # We can resolve on this literal
            new_literals = (clause1.literals - {lit1}) | (clause2.literals - {neg_lit1})
            resolvents.append(Clause(new_literals))
    
    return resolvents

def resolution_theorem_proving(kb, query):
    """
    Resolution-based theorem proving
    Returns: (result, derivation_steps)
    """
    # Convert KB sentences to CNF and extract clauses
    clauses = set()
    
    for sentence in kb.sentences:
        cnf = convert_to_cnf(sentence)
        sentence_clauses = extract_clauses_from_cnf(cnf)
        clauses.update(sentence_clauses)
    
    # Add negation of query to prove by contradiction
    # If query is 'p', add clause containing '~p'
    negated_query = Clause({'~' + query})
    clauses.add(negated_query)
    
    derivation_steps = []
    new_clauses = set()
    
    while True:
        # Try to resolve all pairs of clauses
        clause_list = list(clauses)
        pairs_to_resolve = []
        
        for i in range(len(clause_list)):
            for j in range(i + 1, len(clause_list)):
                pairs_to_resolve.append((clause_list[i], clause_list[j]))
        
        # Resolve each pair
        for clause1, clause2 in pairs_to_resolve:
            resolvents = resolve(clause1, clause2)
            
            for resolvent in resolvents:
                derivation_steps.append(f"Resolved {clause1} and {clause2} to get {resolvent}")
                
                if resolvent.is_empty():
                    # Found contradiction - query is entailed
                    return True, derivation_steps
                
                new_clauses.add(resolvent)
        
        # If no new clauses were generated, we can't prove the query
        if new_clauses.issubset(clauses):
            return False, derivation_steps
        
        clauses.update(new_clauses)