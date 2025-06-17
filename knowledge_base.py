# utils/knowledge_base.py
#Test push
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
    Stores facts and rules parsed from the TELL section.
    """
    def __init__(self):
        self.facts = set()  # known true propositions
        self.rules = []     # list of Rule objects

    def add_fact(self, fact):
        self.facts.add(fact)

    def add_rule(self, rule):
        self.rules.append(rule)
