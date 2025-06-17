# algorithms/backward_chaining.py

def backward_chaining(kb, query):
    """
    Backward Chaining Algorithm.
    kb: KnowledgeBase object
    query: proposition symbol to be proved
    """
    visited = set()  # To avoid infinite loops
    entailed = []    # Track the order of inference
    
    def bc_recursive(goal):
        """
        Recursive helper function for backward chaining.
        Returns True if goal can be proven, False otherwise.
        """
        # Avoid infinite loops
        if goal in visited:
            return False
        
        visited.add(goal)
        
        # Check if goal is already a known fact
        if goal in kb.facts:
            if goal not in entailed:
                entailed.append(goal)
            return True
        
        # Try to prove goal using rules
        for rule in kb.rules:
            if rule.conclusion == goal:
                # Try to prove all premises of this rule
                all_premises_proven = True
                temp_entailed = []  # Temporary list to track premises for this rule
                
                for premise in rule.premises:
                    if not bc_recursive(premise):
                        all_premises_proven = False
                        break
                    else:
                        if premise not in temp_entailed:
                            temp_entailed.append(premise)
                
                if all_premises_proven:
                    # Add premises to entailed list if not already there
                    for premise in temp_entailed:
                        if premise not in entailed:
                            entailed.append(premise)
                    
                    # Add the goal (conclusion) to entailed list
                    if goal not in entailed:
                        entailed.append(goal)
                    
                    return True
        
        return False
    
    # Start the backward chaining process
    result = bc_recursive(query)
    
    return result, entailed