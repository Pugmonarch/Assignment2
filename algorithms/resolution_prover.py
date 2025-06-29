# resolution_prover.py
# Enhanced resolution-based theorem prover with complete CNF conversion

from parser import *
from knowledge_base import *

class Clause:
    """Represents a clause (disjunction of literals)"""
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

def negate_literal(literal):
    """Negate a literal"""
    if literal.startswith('~'):
        return literal[1:]  # Remove negation
    else:
        return '~' + literal  # Add negation

def convert_to_cnf(expr):
    """Convert a logical expression to Conjunctive Normal Form (CNF)"""
    
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
        """Apply De Morgan's laws and double negation elimination"""
        if isinstance(expr, Negation):
            if isinstance(expr.operand, Negation):
                # Double negation elimination: ~~p becomes p
                return move_negations_inward(expr.operand.operand)
            elif isinstance(expr.operand, Conjunction):
                # De Morgan's law: ~(p & q) becomes ~p || ~q
                left = move_negations_inward(Negation(expr.operand.left))
                right = move_negations_inward(Negation(expr.operand.right))
                return Disjunction(left, right)
            elif isinstance(expr.operand, Disjunction):
                # De Morgan's law: ~(p || q) becomes ~p & ~q
                left = move_negations_inward(Negation(expr.operand.left))
                right = move_negations_inward(Negation(expr.operand.right))
                return Conjunction(left, right)
            else:
                # Negation of atom - keep as is
                return expr
        elif isinstance(expr, BinaryExpression):
            return type(expr)(move_negations_inward(expr.left), 
                            move_negations_inward(expr.right))
        else:
            return expr
    
    def distribute_or_over_and(expr):
        """Distribute OR over AND to get CNF: (A || (B & C)) becomes (A || B) & (A || C)"""
        if isinstance(expr, Disjunction):
            left = distribute_or_over_and(expr.left)
            right = distribute_or_over_and(expr.right)
            
            # Check if we need to distribute
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
        """Recursively extract clauses from conjunction"""
        if isinstance(expr, Conjunction):
            extract_from_conjunction(expr.left)
            extract_from_conjunction(expr.right)
        else:
            # This should be a disjunction or a single literal
            literals = extract_literals_from_disjunction(expr)
            if literals:  # Only add non-empty clauses
                clauses.append(Clause(literals))
    
    def extract_literals_from_disjunction(expr):
        """Extract literals from a disjunction or single literal"""
        literals = []
        
        def collect_literals(e):
            if isinstance(e, Disjunction):
                collect_literals(e.left)
                collect_literals(e.right)
            elif isinstance(e, Negation) and isinstance(e.operand, Atom):
                literals.append('~' + e.operand.symbol)
            elif isinstance(e, Atom):
                literals.append(e.symbol)
            else:
                # Handle other cases - this shouldn't happen in proper CNF
                literals.append(str(e))
        
        collect_literals(expr)
        return literals
    
    # Handle the case where the entire expression is a single clause
    if isinstance(cnf_expr, (Atom, Negation)) or isinstance(cnf_expr, Disjunction):
        literals = extract_literals_from_disjunction(cnf_expr)
        if literals:
            clauses.append(Clause(literals))
    else:
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
            resolvent = Clause(new_literals)
            resolvents.append(resolvent)
    
    return resolvents

def convert_horn_kb_to_clauses(kb):
    """Convert Horn clause knowledge base to resolution clauses"""
    clauses = set()
    
    # Convert facts to unit clauses
    for fact in kb.facts:
        clauses.add(Clause([fact]))
    
    # Convert rules to clauses
    for rule in kb.rules:
        # Convert p & q => r to ~p || ~q || r
        literals = ['~' + premise for premise in rule.premises] + [rule.conclusion]
        clauses.add(Clause(literals))
    
    return clauses

def convert_general_kb_to_clauses(kb):
    """Convert general knowledge base to resolution clauses"""
    clauses = set()
    
    for sentence in kb.sentences:
        # Convert each sentence to CNF and extract clauses
        cnf = convert_to_cnf(sentence)
        sentence_clauses = extract_clauses_from_cnf(cnf)
        clauses.update(sentence_clauses)
    
    return clauses

def resolution_theorem_proving(kb, query):
    """
    Resolution-based theorem proving
    Returns: (result, derivation_steps)
    """
    # Convert KB to clauses based on type
    if hasattr(kb, 'sentences'):  # GeneralKnowledgeBase
        clauses = convert_general_kb_to_clauses(kb)
    else:  # Horn clause KnowledgeBase
        clauses = convert_horn_kb_to_clauses(kb)
    
    # Add negation of query to prove by contradiction
    negated_query = Clause(['~' + query])
    clauses.add(negated_query)
    
    derivation_steps = []
    iteration = 0
    max_iterations = 1000  # Prevent infinite loops
    
    while iteration < max_iterations:
        iteration += 1
        clause_list = list(clauses)
        new_clauses = set()
        
        # Try to resolve all pairs of clauses
        for i in range(len(clause_list)):
            for j in range(i + 1, len(clause_list)):
                clause1, clause2 = clause_list[i], clause_list[j]
                resolvents = resolve(clause1, clause2)
                
                for resolvent in resolvents:
                    derivation_steps.append(f"Iteration {iteration}: Resolved {clause1} and {clause2} to get {resolvent}")
                    
                    if resolvent.is_empty():
                        # Found contradiction - query is entailed
                        derivation_steps.append(f"Empty clause derived - proof complete!")
                        return True, derivation_steps
                    
                    new_clauses.add(resolvent)
        
        # If no new clauses were generated, we can't prove the query
        if new_clauses.issubset(clauses):
            derivation_steps.append(f"No new clauses generated after {iteration} iterations - cannot prove query")
            return False, derivation_steps
        
        clauses.update(new_clauses)
        
        # Optional: limit clause set size to prevent explosion
        if len(clauses) > 10000:
            derivation_steps.append("Clause set too large - terminating")
            return False, derivation_steps
    
    derivation_steps.append(f"Maximum iterations ({max_iterations}) reached")
    return False, derivation_steps

def print_cnf_conversion_steps(expr):
    """Helper function to print CNF conversion steps for debugging"""
    print(f"Original: {expr}")
    
    # Step 1: Eliminate biconditionals
    step1 = expr
    if any(isinstance(e, Biconditional) for e in get_all_subexpressions(expr)):
        from copy import deepcopy
        step1 = eliminate_biconditionals_debug(deepcopy(expr))
        print(f"After eliminating biconditionals: {step1}")
    
    # Step 2: Eliminate implications
    step2 = step1
    if any(isinstance(e, Implication) for e in get_all_subexpressions(step1)):
        step2 = eliminate_implications_debug(step1)
        print(f"After eliminating implications: {step2}")
    
    # Step 3: Move negations inward
    step3 = move_negations_inward_debug(step2)
    print(f"After moving negations inward: {step3}")
    
    # Step 4: Distribute OR over AND
    step4 = distribute_or_over_and_debug(step3)
    print(f"Final CNF: {step4}")
    
    return step4

def get_all_subexpressions(expr):
    """Get all subexpressions of an expression"""
    if isinstance(expr, Atom):
        return [expr]
    elif isinstance(expr, Negation):
        return [expr] + get_all_subexpressions(expr.operand)
    elif isinstance(expr, BinaryExpression):
        return [expr] + get_all_subexpressions(expr.left) + get_all_subexpressions(expr.right)
    else:
        return [expr]

# Debug versions of transformation functions (same logic, just for debugging)
def eliminate_biconditionals_debug(expr):
    """Debug version of eliminate_biconditionals"""
    # Same implementation as in convert_to_cnf
    if isinstance(expr, Biconditional):
        left_to_right = Implication(expr.left, expr.right)
        right_to_left = Implication(expr.right, expr.left)
        return Conjunction(left_to_right, right_to_left)
    elif isinstance(expr, BinaryExpression):
        return type(expr)(eliminate_biconditionals_debug(expr.left), 
                        eliminate_biconditionals_debug(expr.right))
    elif isinstance(expr, Negation):
        return Negation(eliminate_biconditionals_debug(expr.operand))
    else:
        return expr

def eliminate_implications_debug(expr):
    """Debug version of eliminate_implications"""
    if isinstance(expr, Implication):
        return Disjunction(Negation(expr.left), expr.right)
    elif isinstance(expr, BinaryExpression):
        return type(expr)(eliminate_implications_debug(expr.left), 
                        eliminate_implications_debug(expr.right))
    elif isinstance(expr, Negation):
        return Negation(eliminate_implications_debug(expr.operand))
    else:
        return expr

def move_negations_inward_debug(expr):
    """Debug version of move_negations_inward"""
    if isinstance(expr, Negation):
        if isinstance(expr.operand, Negation):
            return move_negations_inward_debug(expr.operand.operand)
        elif isinstance(expr.operand, Conjunction):
            left = move_negations_inward_debug(Negation(expr.operand.left))
            right = move_negations_inward_debug(Negation(expr.operand.right))
            return Disjunction(left, right)
        elif isinstance(expr.operand, Disjunction):
            left = move_negations_inward_debug(Negation(expr.operand.left))
            right = move_negations_inward_debug(Negation(expr.operand.right))
            return Conjunction(left, right)
        else:
            return expr
    elif isinstance(expr, BinaryExpression):
        return type(expr)(move_negations_inward_debug(expr.left), 
                        move_negations_inward_debug(expr.right))
    else:
        return expr

def distribute_or_over_and_debug(expr):
    """Debug version of distribute_or_over_and"""
    if isinstance(expr, Disjunction):
        left = distribute_or_over_and_debug(expr.left)
        right = distribute_or_over_and_debug(expr.right)
        
        if isinstance(left, Conjunction):
            a_or_right = distribute_or_over_and_debug(Disjunction(left.left, right))
            b_or_right = distribute_or_over_and_debug(Disjunction(left.right, right))
            return Conjunction(a_or_right, b_or_right)
        elif isinstance(right, Conjunction):
            left_or_b = distribute_or_over_and_debug(Disjunction(left, right.left))
            left_or_c = distribute_or_over_and_debug(Disjunction(left, right.right))
            return Conjunction(left_or_b, left_or_c)
        else:
            return Disjunction(left, right)
    elif isinstance(expr, Conjunction):
        return Conjunction(distribute_or_over_and_debug(expr.left), 
                         distribute_or_over_and_debug(expr.right))
    elif isinstance(expr, Negation):
        return Negation(distribute_or_over_and_debug(expr.operand))
    else:
        return expr