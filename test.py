#!/usr/bin/env python3
"""
Test management script for Apstra MCP Server
Usage: python test.py [command]

Commands:
  run       - Run all tests (default)
  unit      - Run unit tests only
  functional - Run functional tests only
  clean     - Clean up test blueprints
  demo      - Run blueprint creation demo
"""

import sys
import os
import subprocess

def run_command(cmd):
    """Run a command and return success status"""
    try:
        result = subprocess.run(cmd, shell=True, cwd=os.path.dirname(__file__))
        return result.returncode == 0
    except Exception as e:
        print(f"Error running command: {e}")
        return False

def main():
    """Main test management function"""
    
    # Get command from arguments
    command = sys.argv[1] if len(sys.argv) > 1 else "run"
    
    print(f"Apstra MCP Server - Test Management")
    print(f"Command: {command}")
    print("=" * 50)
    
    if command == "run":
        print("Running all tests...")
        success = run_command("python tests/run_tests.py")
        
    elif command == "unit":
        print("Running unit tests only...")
        success = run_command("python -m unittest tests.test_unit -v")
        
    elif command == "functional":
        print("Running functional tests only...")
        success = run_command("python -m unittest tests.test_functional -v")
        
    elif command == "clean":
        print("Cleaning up test blueprints...")
        success = run_command("python tests/test_cleanup.py")
        
    elif command == "demo":
        print("Running blueprint creation demo...")
        success = run_command("python demo_blueprint_creation.py")
        
    elif command == "help" or command == "--help" or command == "-h":
        print(__doc__)
        return 0
        
    else:
        print(f"Unknown command: {command}")
        print("Use 'python test.py help' for available commands")
        return 1
    
    print("\n" + "=" * 50)
    if success:
        print(f"✓ {command.title()} completed successfully")
        return 0
    else:
        print(f"✗ {command.title()} failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())