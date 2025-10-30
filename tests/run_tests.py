"""
Test runner for RISC-V, runs all unit tests
"""

import unittest
import sys
import os
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_all_tests():
    print("RISC-V Unit Test")
    print("=" * 60)
    print()
    
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(os.path.abspath(__file__))
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    runner = unittest.TextTestRunner(
        verbosity=2,
        descriptions=True,
        failfast=False
    )
    
    print("Running all unit tests...")
    print("-" * 40)
    
    start_time = time.time()
    result = runner.run(suite)
    end_time = time.time()
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    skipped = len(result.skipped) if hasattr(result, 'skipped') else 0
    passed = total_tests - failures - errors - skipped
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed}")
    print(f"Failed: {failures}")
    print(f"Errors: {errors}")
    print(f"Skipped: {skipped}")
    print(f"Success Rate: {(passed / total_tests) * 100:.1f}%")
    print(f"Execution Time: {end_time - start_time:.2f} seconds")
    
    if failures > 0:
        print("\n" + "=" * 60)
        print("FAILURES")
        print("=" * 60)
        for test, traceback in result.failures:
            print(f"\nFAILED: {test}")
            print("-" * 40)
            print(traceback)
    
    if errors > 0:
        print("\n" + "=" * 60)
        print("ERRORS")
        print("=" * 60)
        for test, traceback in result.errors:
            print(f"\nERROR: {test}")
            print("-" * 40)
            print(traceback)
    
    print("\n" + "=" * 60)
    print("COMPONENT COVERAGE")
    print("=" * 60)
    
    components = [
        ("Two's Complement", "test_twos_complement.py"),
        ("ALU", "test_alu.py"),
        ("Multiply/Divide", "test_mdu.py"),
        ("IEEE-754 Float32", "test_fpu_f32.py"),
    ]
    
    for component_name, test_file in components:
        test_path = os.path.join(start_dir, test_file)
        if os.path.exists(test_path):
            print(f"{component_name}: {test_file}")
        else:
            print(f"{component_name}: {test_file} (missing)")
    
    if failures == 0 and errors == 0:
        print("\nAll tests passed")
        return True
    else:
        print(f"\n{failures + errors} test(s) failed")
        return False

def run_specific_test(test_name):
    print(f"Running {test_name}...")
    print("-" * 40)
    
    test_module = __import__(test_name.replace('.py', ''))
    suite = unittest.TestLoader().loadTestsFromModule(test_module)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

def main():
    if len(sys.argv) > 1:
        test_name = sys.argv[1]
        success = run_specific_test(test_name)
    else:
        success = run_all_tests()
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()

