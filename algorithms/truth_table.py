# Fixed truth_table.py - Key issues resolved

from itertools import product
from knowledge_base import *

def truth_table(kb, query):
    """
    Truth Table Method - works with both Horn clauses and general propositional logic
    kb: KnowledgeBase or GeneralKnowledgeBase object  
    query: proposition symbol to be proved
    Returns: (result, number_of_models) where result is True/False and number_of_models is count of valid models
    """
    if isinstance(kb, GeneralKnowledgeBase):
        return general_truth_table(kb, query)
    else:
        return horn_truth_table(kb, query)

def general_truth_table(kb, query):
    """Truth table method for general propositional logic - FIXED VERSION"""
    # Collect all atoms from the knowledge base and query
    all_atoms = set()
    
    for sentence in kb.sentences:
        all_atoms.update(extract_atoms_from_expr(sentence))
    
    # CRITICAL FIX: Handle query properly - it might be a complex expression
    if hasattr(query, 'symbol'):  # It's an Atom object
        all_atoms.add(query.symbol)
        query_symbol = query.symbol
    elif isinstance(query, str):  # It's a string
        all_atoms.add(query)
        query_symbol = query
    else:  # It's a complex expression
        all_atoms.update(extract_atoms_from_expr(query))
        query_symbol = None  # We'll evaluate the full expression
    
    # Convert to sorted list for consistent ordering
    atoms = sorted(list(all_atoms))
    
    # Early termination for large problems
    if len(atoms) > 25:
        return None, f"Too many variables ({len(atoms)}) for truth table method."
    
    # Generate all possible truth value assignments
    valid_models = []
    
    # Check each possible truth assignment
    for values in product([True, False], repeat=len(atoms)):
        model = dict(zip(atoms, values))
        
        # Check if this model satisfies ALL sentences in the knowledge base
        if satisfies_general_kb(kb, model):
            valid_models.append(model)
    
    # Handle inconsistent KB
    if not valid_models:
        # If KB is inconsistent (no satisfying models), it entails everything
        return True, 0
    
    # CRITICAL FIX: Proper query evaluation
    if query_symbol:
        # Simple query - just check the symbol
        query_true_models = sum(1 for model in valid_models if model.get(query_symbol, False))
    else:
        # Complex query - evaluate the full expression
        query_true_models = sum(1 for model in valid_models if evaluate_expression(query, model))
    
    # Query is entailed iff it's true in ALL models that satisfy the KB
    result = query_true_models == len(valid_models)
    
    return result, len(valid_models)

def satisfies_general_kb(kb, model):
    """Check if a model satisfies all sentences in the general knowledge base"""
    for sentence in kb.sentences:
        if not evaluate_expression(sentence, model):
            return False
    return True

def evaluate_expression(expr, model):
    """Evaluate a logical expression given a truth assignment - IMPROVED VERSION"""
    if isinstance(expr, Atom):
        return model.get(expr.symbol, False)
    
    elif isinstance(expr, Negation):
        return not evaluate_expression(expr.operand, model)
    
    elif isinstance(expr, Conjunction):
        left_val = evaluate_expression(expr.left, model)
        right_val = evaluate_expression(expr.right, model)
        return left_val and right_val
    
    elif isinstance(expr, Disjunction):
        left_val = evaluate_expression(expr.left, model)
        right_val = evaluate_expression(expr.right, model)
        return left_val or right_val
    
    elif isinstance(expr, Implication):
        # p => q is equivalent to ~p || q
        left_val = evaluate_expression(expr.left, model)
        right_val = evaluate_expression(expr.right, model)
        return (not left_val) or right_val
    
    elif isinstance(expr, Biconditional):
        # p <=> q is true iff p and q have the same truth value
        left_val = evaluate_expression(expr.left, model)
        right_val = evaluate_expression(expr.right, model)
        return left_val == right_val
    
    else:
        raise ValueError(f"Unknown expression type: {type(expr)}")

def extract_atoms_from_expr(expr):
    """Extract all atomic propositions from a logical expression"""
    atoms = set()
    
    def collect_atoms(e):
        if isinstance(e, Atom):
            atoms.add(e.symbol)
        elif isinstance(e, Negation):
            collect_atoms(e.operand)
        elif hasattr(e, 'left') and hasattr(e, 'right'):  # Binary expressions
            collect_atoms(e.left)
            collect_atoms(e.right)
    
    collect_atoms(expr)
    return atoms

def horn_truth_table(kb, query):
    """Truth table for Horn clause knowledge base"""
    # Get all unique symbols from facts and rules
    symbols = set()
    
    # Add symbols from facts
    symbols.update(kb.facts)
    
    # Add symbols from rules
    for rule in kb.rules:
        symbols.update(rule.premises)
        symbols.add(rule.conclusion)
    
    # Add query symbol
    symbols.add(query)
    
    # Convert to sorted list for consistent ordering
    symbols = sorted(list(symbols))
    
    # Early termination if too many symbols
    if len(symbols) > 25:
        return None, f"Too many variables ({len(symbols)}) for truth table method."
    
    # Generate all possible truth value assignments
    valid_models = []
    
    # Check each possible truth assignment
    for values in product([True, False], repeat=len(symbols)):
        model = dict(zip(symbols, values))
        
        # Check if this model satisfies the knowledge base
        if satisfies_horn_kb(kb, model):
            valid_models.append(model)
    
    # Handle inconsistent KB
    if not valid_models:
        return True, 0
    
    # Count models where query is true
    query_true_models = sum(1 for model in valid_models if model.get(query, False))
    
    # Query is entailed iff it's true in ALL valid models
    result = query_true_models == len(valid_models)
    
    return result, len(valid_models)

def satisfies_horn_kb(kb, model):
    """Check if a given model satisfies the Horn clause knowledge base"""
    # Check if all facts are true in the model
    for fact in kb.facts:
        if not model.get(fact, False):
            return False
    
    # Check if all rules are satisfied
    for rule in kb.rules:
        # A rule (premises => conclusion) is satisfied if:
        # either some premise is false OR conclusion is true
        premises_true = all(model.get(premise, False) for premise in rule.premises)
        
        if premises_true and not model.get(rule.conclusion, False):
            return False
    
    return True
