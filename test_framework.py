# test_framework.py - Fixed and enhanced testing framework for inference engine

import time
import subprocess
import os
import glob
from typing import Dict, List, Tuple, Any

class TestFramework:
    """Automated testing framework for the inference engine"""
    
    def __init__(self, engine_path="iengine.py", test_folder="tests"):
        self.engine_path = engine_path
        self.test_folder = test_folder
        self.test_results = []
        self.debug_mode = False
    
    def set_debug_mode(self, debug=True):
        """Enable/disable debug mode for detailed output"""
        self.debug_mode = debug
    
    def discover_test_files(self) -> List[str]:
        """Discover all test files in the test folder"""
        if not os.path.exists(self.test_folder):
            print(f"Warning: Test folder '{self.test_folder}' does not exist")
            return []
        
        # Look for .txt files in the test folder
        pattern = os.path.join(self.test_folder, "*.txt")
        test_files = glob.glob(pattern)
        
        if not test_files:
            print(f"Warning: No .txt test files found in '{self.test_folder}'")
        
        return sorted(test_files)
    
    def run_inference_engine(self, test_file: str, method: str) -> Tuple[bool, str]:
        """Run the inference engine and return (success, output)"""
        try:
            cmd = ["python3", self.engine_path, test_file, method]
            if self.debug_mode:
                print(f"    Running command: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                output = result.stdout.strip()
                if self.debug_mode:
                    print(f"    Raw output: '{output}'")
                
                # Check if output contains valid result (YES or NO at start)
                if output and (output.startswith("YES") or output.startswith("NO")):
                    return True, output
                else:
                    return False, f"Invalid output format: {output[:100]}..."
            else:
                error_msg = result.stderr.strip() if result.stderr.strip() else result.stdout.strip()
                if self.debug_mode:
                    print(f"    Error output: '{error_msg}'")
                return False, f"Process error: {error_msg[:100]}..."
                
        except subprocess.TimeoutExpired:
            return False, "TIMEOUT: Process exceeded 30 seconds"
        except FileNotFoundError:
            return False, f"ERROR: Could not find {self.engine_path}"
        except Exception as e:
            return False, f"Exception: {str(e)}"
    
    def extract_result(self, output: str) -> str:
        """Extract YES/NO result from output"""
        if not output:
            return "ERROR"
        
        # Handle error cases
        if any(output.startswith(prefix) for prefix in ["ERROR", "TIMEOUT", "Exception", "Process error", "Invalid output"]):
            return "ERROR"
        
        # Extract result
        if output.startswith("YES"):
            return "YES"
        elif output.startswith("NO"):
            return "NO"
        else:
            return "UNKNOWN"
    
    def validate_consistency(self, results: Dict[str, str], test_name: str) -> Tuple[bool, str]:
        """Check if all successful methods give consistent YES/NO results"""
        # Extract YES/NO results from successful runs
        outcomes = {}
        for method, output in results.items():
            result = self.extract_result(output)
            if result in ["YES", "NO"]:
                outcomes[method] = result
        
        if len(outcomes) == 0:
            return False, "No successful methods"
        elif len(set(outcomes.values())) == 1:
            consensus = list(outcomes.values())[0]
            return True, f"Consistent: {consensus}"
        else:
            # Find disagreements
            disagreements = []
            unique_results = set(outcomes.values())
            for result in unique_results:
                methods_with_result = [m for m, r in outcomes.items() if r == result]
                disagreements.append(f"{result}: {', '.join(methods_with_result)}")
            
            return False, f"Inconsistent: {' vs '.join(disagreements)}"
    
    def run_single_test(self, test_file: str, test_name: str = None) -> Dict[str, Any]:
        """Run a single test file with all applicable methods"""
        if test_name is None:
            test_name = os.path.basename(test_file)
        
        print(f"\nRunning {test_name} ({test_file})...")
        
        # Standard inference methods
        methods = ['TT', 'FC', 'BC', 'RES']
        results = {}
        timings = {}
        
        for method in methods:
            print(f"  Running {method}...", end=" ")
            
            start_time = time.time()
            success, output = self.run_inference_engine(test_file, method)
            end_time = time.time()
            
            results[method] = output
            timings[method] = end_time - start_time
            
            # Show individual results
            if success:
                result = self.extract_result(output)
                print(f"✓ {result} ({timings[method]:.3f}s)")
            else:
                error_msg = output[:50] + ('...' if len(output) > 50 else '')
                print(f"✗ {error_msg} ({timings[method]:.3f}s)")
        
        # Validate consistency
        consistent, consistency_msg = self.validate_consistency(results, test_name)
        print(f"  ✓ {test_name}: {consistency_msg}")
        
        # Special handling for inconsistent results - show details
        if not consistent and "Inconsistent" in consistency_msg:
            print(f"    ⚠️  INCONSISTENCY DETECTED:")
            for method, output in results.items():
                result = self.extract_result(output)
                if result in ["YES", "NO"]:
                    print(f"      {method}: {result}")
            
            # If this is a problematic test, suggest debugging
            if any(name in test_name.lower() for name in ['demorgan', 'biconditional', 'complex', 'negation']):
                print(f"    💡 This test involves complex logic - consider running debug mode")
        
        test_result = {
            'name': test_name,
            'file': test_file,
            'results': results,
            'timings': timings,
            'consistent': consistent,
            'consistency_msg': consistency_msg
        }
        
        self.test_results.append(test_result)
        return test_result

    def run_all_tests(self):
        """Run all tests found in the test folder"""
        test_files = self.discover_test_files()
        
        if not test_files:
            print("No test files found to run!")
            return
        
        print(f"=== Running All Tests from '{self.test_folder}' ===")
        print(f"Found {len(test_files)} test files")
        
        for test_file in test_files:
            # Create a nice test name from filename
            test_name = os.path.splitext(os.path.basename(test_file))[0]
            self.run_single_test(test_file, test_name)

    def generate_chain_kb(self, length: int) -> str:
        """Generate a knowledge base with a chain of implications for performance testing"""
        kb_content = "TELL\n"
        
        # Create chain: p1 => p2 => p3 => ... => p{length}
        for i in range(1, length):
            kb_content += f"p{i} => p{i+1}\n"
        
        # Add initial fact
        kb_content += "p1\n"
        kb_content += f"\nASK\np{length}\n"
        
        return kb_content
    
    def run_performance_tests(self):
        """Run performance benchmarking tests"""
        print("\n=== Performance Tests ===")
        test_sizes = [5, 10, 25, 50]
        
        for size in test_sizes:
            # Generate test file
            kb_content = self.generate_chain_kb(size)
            temp_file = f"temp_chain_{size}.txt"
            
            try:
                with open(temp_file, 'w') as f:
                    f.write(kb_content)
                
                self.run_single_test(temp_file, f"Performance_Chain_Length_{size}")
                
            finally:
                # Clean up temp file
                if os.path.exists(temp_file):
                    os.remove(temp_file)
    
    def identify_problematic_tests(self) -> Dict[str, List[str]]:
        """Identify and categorize problematic tests"""
        problems = {
            'inconsistent': [],
            'all_failed': [],
            'tt_specific': [],
            'complex_logic': []
        }
        
        for result in self.test_results:
            name = result['name']
            
            # Check if inconsistent
            if not result['consistent'] and "Inconsistent" in result['consistency_msg']:
                problems['inconsistent'].append(name)
                
                # Check if TT is the problem
                tt_result = self.extract_result(result['results'].get('TT', ''))
                other_results = [self.extract_result(result['results'].get(m, '')) 
                               for m in ['FC', 'BC', 'RES'] if self.extract_result(result['results'].get(m, '')) in ['YES', 'NO']]
                
                if tt_result in ['YES', 'NO'] and other_results and all(r != tt_result for r in other_results):
                    problems['tt_specific'].append(name)
            
            # Check if all methods failed
            if result['consistency_msg'] == "No successful methods":
                problems['all_failed'].append(name)
            
            # Check for complex logic tests
            if any(keyword in name.lower() for keyword in ['demorgan', 'biconditional', 'complex', 'deep', 'negation']):
                problems['complex_logic'].append(name)
        
        return problems
    
    def generate_report(self):
        """Generate a comprehensive test report"""
        print("\n" + "="*70)
        print("INFERENCE ENGINE TEST REPORT")
        print("="*70)
        
        if not self.test_results:
            print("No test results to report!")
            return
        
        total_tests = len(self.test_results)
        consistent_tests = sum(1 for r in self.test_results if r['consistent'])
        
        print(f"Total Tests Run: {total_tests}")
        print(f"Consistent Results: {consistent_tests}/{total_tests} ({(consistent_tests/total_tests)*100:.1f}%)")
        
        # Method performance summary
        print("\n--- Method Performance Summary ---")
        methods = ['TT', 'FC', 'BC', 'RES']
        
        for method in methods:
            successful_runs = 0
            total_time = 0
            error_count = 0
            timeout_count = 0
            
            for result in self.test_results:
                if method in result['timings']:
                    total_time += result['timings'][method]
                    method_result = self.extract_result(result['results'][method])
                    
                    if method_result in ["YES", "NO"]:
                        successful_runs += 1
                    elif method_result == "ERROR":
                        if "TIMEOUT" in result['results'][method]:
                            timeout_count += 1
                        else:
                            error_count += 1
            
            avg_time = total_time / total_tests if total_tests > 0 else 0
            success_rate = (successful_runs / total_tests) * 100 if total_tests > 0 else 0
            
            status_info = []
            if timeout_count > 0:
                status_info.append(f"{timeout_count} timeouts")
            if error_count > 0:
                status_info.append(f"{error_count} errors")
            
            status_str = f" ({', '.join(status_info)})" if status_info else ""
            print(f"{method:10}: {success_rate:5.1f}% success, avg {avg_time:.3f}s per test{status_str}")
        
        # Analyze problematic tests
        problems = self.identify_problematic_tests()
        
        if problems['inconsistent']:
            print(f"\n--- Inconsistent Tests ({len(problems['inconsistent'])}) ---")
            for test_name in problems['inconsistent']:
                test_result = next(r for r in self.test_results if r['name'] == test_name)
                print(f"⚠️  {test_name}: {test_result['consistency_msg']}")
                
                # Show the actual disagreement
                for method in ['TT', 'FC', 'BC', 'RES']:
                    if method in test_result['results']:
                        result = self.extract_result(test_result['results'][method])
                        if result in ['YES', 'NO']:
                            print(f"     {method}: {result}")
        
        
        if problems['complex_logic']:
            print(f"\n--- Complex Logic Tests ({len(problems['complex_logic'])}) ---")
            print("These tests involve complex logical expressions:")
            for test_name in problems['complex_logic']:
                status = "✓" if any(r['name'] == test_name and r['consistent'] for r in self.test_results) else "⚠️"
                print(f"{status} {test_name}")
        
        if problems['all_failed']:
            print(f"\n--- Completely Failed Tests ({len(problems['all_failed'])}) ---")
            for test_name in problems['all_failed']:
                print(f"❌ {test_name}: All methods failed")
      

    def run_debug_session(self, test_name: str):
        """Run a specific test in debug mode with detailed output"""
        print(f"\n=== DEBUG SESSION FOR: {test_name} ===")
        
        # Find the test file
        test_file = None
        for result in self.test_results:
            if result['name'] == test_name:
                test_file = result['file']
                break
        
        if not test_file:
            # Try to find it in the test folder
            potential_file = os.path.join(self.test_folder, f"{test_name}.txt")
            if os.path.exists(potential_file):
                test_file = potential_file
        
        if not test_file:
            print(f"Could not find test file for {test_name}")
            return
        
        print(f"Test file: {test_file}")
        
        # Show the test file content
        try:
            with open(test_file, 'r') as f:
                content = f.read()
            print(f"\nTest file content:")
            print("-" * 40)
            print(content)
            print("-" * 40)
        except Exception as e:
            print(f"Could not read test file: {e}")
        
        # Run with debug mode
        old_debug = self.debug_mode
        self.debug_mode = True
        
        try:
            self.run_single_test(test_file, test_name)
        finally:
            self.debug_mode = old_debug

    def run_full_suite(self):
        """Run the complete test suite"""
        print("Starting Inference Engine Test Suite...")
        print("="*60)
        
        # Check if inference engine exists
        if not os.path.exists(self.engine_path):
            print(f"ERROR: Inference engine '{self.engine_path}' not found!")
            return
        
        # Run all discovered tests
        self.run_all_tests()
        
        # Run performance tests
        self.run_performance_tests()
        
        # Generate final report
        self.generate_report()

def main():
    """Main function to run the test framework"""
    import sys
    
    # You can customize these paths
    engine_path = "iengine.py"  # Path to your inference engine
    test_folder = "tests"       # Folder containing test files
    
    framework = TestFramework(engine_path, test_folder)
    
    # Handle command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "debug":
            if len(sys.argv) > 2:
                test_name = sys.argv[2]
                framework.run_debug_session(test_name)
            else:
                print("Usage: python3 test_framework.py debug <test_name>")
        elif command == "quick":
            # Run without performance tests
            framework.run_all_tests()
            framework.generate_report()
        else:
            print("Unknown command. Use 'debug <test_name>' or 'quick'")
    else:
        # Run full suite
        framework.run_full_suite()

if __name__ == "__main__":
    main()