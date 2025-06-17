# iengine.py
#Test push

# hello from Ivan
import sys
import os
from parser import parse_file
from knowledge_base import KnowledgeBase
from algorithms import forward_chaining

def main():
    if len(sys.argv) != 3:
        print("Usage: python iengine.py <filename> <method>")
        return

    filename = sys.argv[1]
    method = sys.argv[2].upper()

    if not os.path.isfile(filename):
        print(f"Error: File '{filename}' not found.")
        return

    kb, query = parse_file(filename)

    if method == "FC":
        result, entailed = forward_chaining.forward_chaining(kb, query)
        if result:
            print("YES:", ', '.join(entailed))
        else:
            print("NO")
    else:
        print("Method not implemented yet!")

if __name__ == "__main__":
    main()
