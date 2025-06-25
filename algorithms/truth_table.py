# truth_table.py - Enhanced to support both Horn clauses and general propositional logic

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

def horn_truth_table(kb, query):
    """Truth table for Horn clause knowledge base (original implementation)"""
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
    
    # Generate all possible truth value assignments
    num_symbols = len(symbols)
    valid_models = []
    
    # Check each possible truth assignment
    for values in product([True, False], repeat=num_symbols):
        model = dict(zip(symbols, values))
        
        # Check if this model satisfies the knowledge base
        if satisfies_horn_kb(kb, model):
            valid_models.append(model)
    
    # Count how many valid models entail the query
    entailing_models = 0
    for model in valid_models:
        if model.get(query, False):
            entailing_models += 1
    
    # The query is entailed if ALL valid models satisfy it
    total_valid_models = len(valid_models)
    if total_valid_models == 0:
        return False, 0
    
    result = entailing_models == total_valid_models
    
    return result, total_valid_models

def satisfies_horn_kb(kb, model):
    """Check if a given model satisfies the Horn clause knowledge base"""
    # Check if all facts are true in the model
    for fact in kb.facts:
        if not model.get(fact, False):
            return False
    
    # Check if all rules are satisfied
    for rule in kb.rules:
        # Check if all premises are true
        premises_true = all(model.get(premise, False) for premise in rule.premises)
        
        # If premises are true, conclusion must also be true
        if premises_true and not model.get(rule.conclusion, False):
            return False
    
    return True

def general_truth_table(kb, query):
    """Truth table method for general propositional logic"""
    # Collect all atoms from the knowledge base and query
    all_atoms = set()
    
    for sentence in kb.sentences:
        all_atoms.update(extract_atoms_from_expr(sentence))
    
    # Add query atom
    all_atoms.add(query)
    
    # Convert to sorted list for consistent ordering
    atoms = sorted(list(all_atoms))
    
    # Generate all possible truth value assignments
    valid_models = []
    
    # Check each possible truth assignment
    for values in product([True, False], repeat=len(atoms)):
        model = dict(zip(atoms, values))
        
        # Check if this model satisfies the knowledge base
        if satisfies_general_kb(kb, model):
            valid_models.append(model)
    
    # Check how many valid models entail the query
    entailing_models = 0
    for model in valid_models:
        if model.get(query, False):
            entailing_models += 1
    
    # Query is entailed if ALL valid models satisfy it
    total_valid_models = len(valid_models)
    if total_valid_models == 0:
        return False, 0
    
    result = (entailing_models == total_valid_models) if total_valid_models > 0 else False
    
    return result, total_valid_models

def satisfies_general_kb(kb, model):
    """Check if a model satisfies all sentences in the general knowledge base"""
    for sentence in kb.sentences:
        if not evaluate_expression(sentence, model):
            return False
    return True

def evaluate_expression(expr, model):
    """Evaluate a logical expression given a truth assignment (model)"""
    if isinstance(expr, Atom):
        return model.get(expr.symbol, False)
    
    elif isinstance(expr, Negation):
        return not evaluate_expression(expr.operand, model)
    
    elif isinstance(expr, Conjunction):
        return evaluate_expression(expr.left, model) and evaluate_expression(expr.right, model)
    
    elif isinstance(expr, Disjunction):
        return evaluate_expression(expr.left, model) or evaluate_expression(expr.right, model)
    
    elif isinstance(expr, Implication):
        # p => q is equivalent to ~p || q
        left_val = evaluate_expression(expr.left, model)
        right_val = evaluate_expression(expr.right, model)
        return (not left_val) or right_val
    
    elif isinstance(expr, Biconditional):
        # p <=> q is equivalent to (p => q) & (q => p)
        left_val = evaluate_expression(expr.left, model)
        right_val = evaluate_expression(expr.right, model)
        return left_val == right_val
    
    else:
        raise ValueError(f"Unknown expression type: {type(expr)}")

def extract_atoms_from_expr(expr):
    """Extract all atomic propositions from a logical expression"""
    atoms = set()
    
    if isinstance(expr, Atom):
        atoms.add(expr.symbol)
    elif isinstance(expr, Negation):
        atoms.update(extract_atoms_from_expr(expr.operand))
    elif hasattr(expr, 'left') and hasattr(expr, 'right'):  # Binary expressions
        atoms.update(extract_atoms_from_expr(expr.left))
        atoms.update(extract_atoms_from_expr(expr.right))
    
    return atoms