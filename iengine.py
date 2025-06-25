# iengine.py - Enhanced with research component
# Supports both Horn clauses and general propositional logic

import sys
import os
from parser import parse_file, extract_atoms
from knowledge_base import KnowledgeBase, GeneralKnowledgeBase
from algorithms import forward_chaining, backward_chaining
from algorithms import truth_table

def find_file(filename):
    """
    Enhanced file finding logic:
    1. Check if file exists as provided
    2. Check in tests/ directory
    3. Return None if not found
    """
    # First, try the filename as provided
    if os.path.isfile(filename):
        return filename
    
    # Then, try in the tests directory
    tests_path = os.path.join("tests", filename)
    if os.path.isfile(tests_path):
        return tests_path
    
    # If neither exists, return None
    return None

def resolution_theorem_proving(kb, query):
    """
    Simple resolution-based theorem prover
    Returns: (result, derivation_info)
    """
    from knowledge_base import Clause
    
    # Convert KB sentences to CNF and extract clauses
    clauses = set()
    
    # For general KB, convert each sentence to clauses
    if isinstance(kb, GeneralKnowledgeBase):
        for sentence in kb.sentences:
            cnf_clauses = convert_to_cnf_clauses(sentence)
            clauses.update(cnf_clauses)
    else:
        # Convert Horn clauses to resolution clauses
        for fact in kb.facts:
            clauses.add(Clause([fact]))
        
        for rule in kb.rules:
            # Convert p & q => r to ~p || ~q || r
            literals = ['~' + premise for premise in rule.premises] + [rule.conclusion]
            clauses.add(Clause(literals))
    
    # Add negation of query to prove by contradiction
    negated_query = Clause(['~' + query])
    clauses.add(negated_query)
    
    # Simple resolution loop
    max_iterations = 100
    iteration = 0
    
    while iteration < max_iterations:
        iteration += 1
        clause_list = list(clauses)
        new_clauses = set()
        
        # Try to resolve all pairs
        for i in range(len(clause_list)):
            for j in range(i + 1, len(clause_list)):
                resolvents = resolve_clauses(clause_list[i], clause_list[j])
                
                for resolvent in resolvents:
                    if resolvent.is_empty():
                        return True, f"Proof found in {iteration} iterations"
                    new_clauses.add(resolvent)
        
        # If no new clauses, we can't prove it
        if new_clauses.issubset(clauses):
            return False, f"No proof found after {iteration} iterations"
        
        clauses.update(new_clauses)
    
    return False, f"Timeout after {max_iterations} iterations"

def convert_to_cnf_clauses(expr):
    """Convert expression to CNF clauses (simplified)"""
    from knowledge_base import Clause, Atom, Negation, Conjunction, Disjunction, Implication
    
    # This is a very simplified CNF conversion
    # A full implementation would be much more complex
    
    if isinstance(expr, Atom):
        return [Clause([expr.symbol])]
    elif isinstance(expr, Negation) and isinstance(expr.operand, Atom):
        return [Clause(['~' + expr.operand.symbol])]
    elif isinstance(expr, Implication):
        # p => q becomes ~p || q
        left_clauses = convert_to_cnf_clauses(Negation(expr.left))
        right_clauses = convert_to_cnf_clauses(expr.right)
        # Combine into disjunction (simplified)
        literals = set()
        for clause in left_clauses:
            literals.update(clause.literals)
        for clause in right_clauses:
            literals.update(clause.literals)
        return [Clause(literals)]
    else:
        # For other cases, return a simple clause
        return [Clause([str(expr)])]

def resolve_clauses(clause1, clause2):
    """Attempt to resolve two clauses"""
    from knowledge_base import Clause
    
    resolvents = []
    
    # Find complementary literals
    for lit1 in clause1.literals:
        if lit1.startswith('~'):
            complement = lit1[1:]  # Remove ~
        else:
            complement = '~' + lit1  # Add ~
        
        if complement in clause2.literals:
            # Resolve on this literal
            new_literals = (clause1.literals - {lit1}) | (clause2.literals - {complement})
            resolvents.append(Clause(new_literals))
    
    return resolvents

def main():
    if len(sys.argv) != 3:
        print("Usage: python iengine.py <filename> <method>")
        print("Methods: FC (Forward Chaining), BC (Backward Chaining), TT (Truth Table), RES (Resolution)")
        print("Note: FC and BC work only with Horn clauses. TT and RES work with general propositional logic.")
        return

    filename = sys.argv[1]
    method = sys.argv[2].upper()

    # Enhanced file finding
    actual_filename = find_file(filename)
    if actual_filename is None:
        print(f"Error: File '{filename}' not found in current directory or tests/ directory.")
        return

    # Parse the file (automatically detects Horn vs General)
    kb, query = parse_file(actual_filename)
    
    # Determine KB type for user feedback
    is_general = isinstance(kb, GeneralKnowledgeBase)
    if is_general:
        print(f"# Detected general propositional logic KB")
    else:
        print(f"# Detected Horn clause KB")

    # Execute the requested method
    if method == "FC":
        if is_general:
            print("Error: Forward Chaining only works with Horn clauses.")
            return
        result, entailed = forward_chaining.forward_chaining(kb, query)
        if result:
            print("YES:", ', '.join(entailed))
        else:
            print("NO")
            
    elif method == "BC":
        if is_general:
            print("Error: Backward Chaining only works with Horn clauses.")
            return
        result, entailed = backward_chaining.backward_chaining(kb, query)
        if result:
            print("YES:", ', '.join(entailed))
        else:
            print("NO")
            
    elif method == "TT":
        # Truth table works with both types
        result, num_models = truth_table.truth_table(kb, query)
        if result:
            print("YES:", num_models)
        else:
            print("NO")
            
    elif method == "RES":
        # Resolution works with both types
        result, info = resolution_theorem_proving(kb, query)
        if result:
            print("YES: Proof by resolution")
            if len(sys.argv) > 3 and sys.argv[3] == "-v":  # Verbose mode
                print(f"# {info}")
        else:
            print("NO")
            if len(sys.argv) > 3 and sys.argv[3] == "-v":  # Verbose mode
                print(f"# {info}")
            
    else:
        print("Method not implemented!")
        print("Available methods: FC (Forward Chaining), BC (Backward Chaining), TT (Truth Table), RES (Resolution)")

if __name__ == "__main__":
    main()