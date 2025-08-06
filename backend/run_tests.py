#!/usr/bin/env python3
"""
Test runner script for the n8n Feedback API
"""
import subprocess
import sys
import os

def run_tests():
    """Run all tests using pytest"""
    print("🧪 Running n8n Feedback API Tests...")
    print("=" * 50)
    
    # Change to backend directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Run pytest
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        "tests/", 
        "-v", 
        "--tb=short",
        "--color=yes"
    ], capture_output=False)
    
    if result.returncode == 0:
        print("\n✅ All tests passed!")
        return True
    else:
        print("\n❌ Some tests failed!")
        return False

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1) 