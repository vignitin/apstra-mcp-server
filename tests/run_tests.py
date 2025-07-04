"""
Test runner script for Apstra MCP Server tests
"""
import unittest
import sys
import os
from io import StringIO

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from test_cleanup import cleanup_all_test_blueprints
from test_config import TEST_SERVER

def run_unit_tests():
    """Run unit tests"""
    print("=" * 60)
    print("RUNNING UNIT TESTS")
    print("=" * 60)
    
    # Discover and run unit tests
    loader = unittest.TestLoader()
    suite = loader.discover('tests', pattern='test_unit.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

def run_functional_tests():
    """Run functional tests"""
    print("\n" + "=" * 60)
    print("RUNNING FUNCTIONAL TESTS")
    print("=" * 60)
    print("Note: These tests run against the real Apstra server at 10.87.2.74")
    print("Ensure the server is accessible and credentials are correct.")
    print("=" * 60)
    
    # Discover and run functional tests
    loader = unittest.TestLoader()
    suite = loader.discover('tests', pattern='test_functional.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

def main():
    """Main test runner"""
    print("Apstra MCP Server Test Suite")
    print("=" * 60)
    
    # Pre-test cleanup
    print("Pre-test cleanup...")
    try:
        cleanup_all_test_blueprints(TEST_SERVER)
    except Exception as e:
        print(f"Warning: Pre-test cleanup failed: {e}")
    
    # Run unit tests first
    unit_success = run_unit_tests()
    
    # Run functional tests
    functional_success = run_functional_tests()
    
    # Post-test cleanup
    print("\nPost-test cleanup...")
    try:
        cleanup_success = cleanup_all_test_blueprints(TEST_SERVER)
        if cleanup_success:
            print("✓ Post-test cleanup completed successfully")
        else:
            print("⚠ Post-test cleanup completed with warnings")
    except Exception as e:
        print(f"✗ Post-test cleanup failed: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Unit Tests: {'PASSED' if unit_success else 'FAILED'}")
    print(f"Functional Tests: {'PASSED' if functional_success else 'FAILED'}")
    
    if unit_success and functional_success:
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed!")
        return 1

if __name__ == '__main__':
    sys.exit(main())