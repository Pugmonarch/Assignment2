# algorithms/forward_chaining.py

from collections import deque

def forward_chaining(kb, query):
    """
    Forward Chaining Algorithm.
    kb: KnowledgeBase object
    query: proposition symbol to be proved
    """
    inferred = set()
    agenda = deque(kb.facts)
    entailed = []

    # Convert rules into easy-to-use structures
    count = {}  # how many premises are still unsatisfied for each rule
    rule_map = {}

    for rule in kb.rules:
        count[rule] = len(rule.premises)
        for premise in rule.premises:
            if premise not in rule_map:
                rule_map[premise] = []
            rule_map[premise].append(rule)

    while agenda:
        symbol = agenda.popleft()
        entailed.append(symbol)

        if symbol == query:
            return True, entailed

        if symbol in rule_map:
            for rule in rule_map[symbol]:
                count[rule] -= 1
                if count[rule] == 0:
                    if rule.conclusion not in inferred:
                        inferred.add(rule.conclusion)
                        agenda.append(rule.conclusion)

    return False, entailed
