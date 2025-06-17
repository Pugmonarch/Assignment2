# iengine.py
#Test push

# testing again
# Hello Ivan
import sys
import os
from parser import parse_file
from knowledge_base import KnowledgeBase
from algorithms import forward_chaining, backward_chaining, truth_table

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

def main():
    if len(sys.argv) != 3:
        print("Usage: python iengine.py <filename> <method>")
        print("Methods: FC (Forward Chaining), BC (Backward Chaining), TT (Truth Table)")
        return

    filename = sys.argv[1]
    method = sys.argv[2].upper()

    # Enhanced file finding
    actual_filename = find_file(filename)
    if actual_filename is None:
        print(f"Error: File '{filename}' not found in current directory or tests/ directory.")
        return

    kb, query = parse_file(actual_filename)

    if method == "FC":
        result, entailed = forward_chaining.forward_chaining(kb, query)
        if result:
            print("YES:", ', '.join(entailed))
        else:
            print("NO")
    elif method == "BC":
        result, entailed = backward_chaining.backward_chaining(kb, query)
        if result:
            print("YES:", ', '.join(entailed))
        else:
            print("NO")
    elif method == "TT":
        result, num_models = truth_table.truth_table(kb, query)
        if result:
            print("YES:", num_models)
        else:
            print("NO")
    else:
        print("Method not implemented yet!")
        print("Available methods: FC (Forward Chaining), BC (Backward Chaining), TT (Truth Table)")

if __name__ == "__main__":
    main()