# algorithms/backward_chaining.py

def backward_chaining(kb, query):
    """
    Backward Chaining Algorithm.
    kb: KnowledgeBase object
    query: proposition symbol to be proved
    """
    entailed = []    # Track the order of inference
    
    def bc_recursive(goal, visited):
        """
        Recursive helper function for backward chaining.
        Returns True if goal can be proven, False otherwise.
        """
        # Avoid infinite loops in this path
        if goal in visited:
            return False
        
        # Check if goal is already a known fact
        if goal in kb.facts:
            if goal not in entailed:
                entailed.append(goal)
            return True
        
        # Try to prove goal using rules
        for rule in kb.rules:
            if rule.conclusion == goal:
                # Create new visited set for this rule attempt
                new_visited = visited | {goal}
                
                # Try to prove all premises of this rule
                all_premises_proven = True
                premises_for_this_rule = []
                
                for premise in rule.premises:
                    if bc_recursive(premise, new_visited):
                        if premise not in premises_for_this_rule:
                            premises_for_this_rule.append(premise)
                    else:
                        all_premises_proven = False
                        break
                
                if all_premises_proven:
                    # Add the goal (conclusion) to entailed list if not already there
                    if goal not in entailed:
                        entailed.append(goal)
                    return True
        
        return False
    
    # Start the backward chaining process
    result = bc_recursive(query, set())
    
    return result, entailed