# parser/kb_parser.py

from knowledge_base import KnowledgeBase, Rule

def parse_file(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()

    kb = KnowledgeBase()
    query = None
    mode = None

    for line in lines:
        line = line.strip()

        if not line:
            continue  # skip empty lines

        if line == "TELL":
            mode = "TELL"
            continue
        elif line == "ASK":
            mode = "ASK"
            continue

        if mode == "TELL":
            parse_tell_line(line, kb)
        elif mode == "ASK":
            query = line.strip()

    return kb, query

def parse_tell_line(line, kb):
    """
    Parses one line inside TELL section.
    """
    if '=>' in line:
        premises_str, conclusion = line.split('=>')
        conclusion = conclusion.strip()
        premises = [p.strip() for p in premises_str.split('&')]
        rule = Rule(premises, conclusion)
        kb.add_rule(rule)
    else:
        # It's a fact
        fact = line.strip()
        kb.add_fact(fact)
