# algorithms/truth_table.py

from itertools import product

def truth_table(kb, query):
    """
    Truth Table Method for propositional logic inference.
    kb: KnowledgeBase object  
    query: proposition symbol to be proved
    Returns: (result, number_of_models) where result is True/False and number_of_models is count of valid models
    """
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
        if satisfies_kb(kb, model):
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
    
    # Return result and number of valid models (as per assignment spec)
    return result, total_valid_models

def satisfies_kb(kb, model):
    """
    Check if a given model (truth assignment) satisfies the knowledge base.
    """
    # Check if all facts are true in the model
    for fact in kb.facts:
        if not model.get(fact, False):
            return False
    
    # Check if all rules are satisfied (if premises are true, conclusion must be true)
    for rule in kb.rules:
        # Check if all premises are true
        premises_true = all(model.get(premise, False) for premise in rule.premises)
        
        # If premises are true, conclusion must also be true
        if premises_true and not model.get(rule.conclusion, False):
            return False
    
    return True