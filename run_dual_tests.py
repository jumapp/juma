#!/usr/bin/env python3
"""
Test runner script for dual testing strategy.
Runs both SQLite quick tests and PostgreSQL full tests.
"""

import os
import sys
import subprocess
import argparse


def run_tests(test_mode: str, test_path: str = "backend/tests/", verbose: bool = True):
    """Run tests with the specified test mode."""
    
    # Set test mode environment variable
    env = os.environ.copy()
    env["TEST_MODE"] = test_mode
    
    # Build pytest command
    cmd = ["python", "-m", "pytest", test_path]
    
    if verbose:
        cmd.append("-v")
    
    # Add test mode specific markers
    if test_mode == "test":
        cmd.extend(["-m", "not slow"])
    elif test_mode == "slow":
        cmd.extend(["-m", "slow"])
    
    cmd.extend(["--tb=short"])
    
    print(f"\n{'='*60}")
    print(f"Running tests with TEST_MODE={test_mode}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*60}\n")
    
    # Run tests
    result = subprocess.run(cmd, env=env, capture_output=False)
    
    return result.returncode == 0


def main():
    parser = argparse.ArgumentParser(description="Run dual testing strategy test suites")
    parser.add_argument(
        "--mode",
        choices=["test", "slow", "both"],
        default="both",
        help="Test mode to run: 'test' (SQLite quick), 'slow' (PostgreSQL full), or 'both'"
    )
    parser.add_argument(
        "--path",
        default="backend/tests/",
        help="Path to test directory"
    )
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Run tests without verbose output"
    )
    
    args = parser.parse_args()
    
    print("="*60)
    print("DUAL TESTING STRATEGY - TEST RUNNER")
    print("="*60)
    
    results = {}
    
    if args.mode in ["test", "both"]:
        print("\nRUNNING SQLITE QUICK TESTS (TEST_MODE=test)")
        results["sqlite"] = run_tests("test", args.path, not args.quiet)
    
    if args.mode in ["slow", "both"]:
        print("\nRUNNING POSTGRESQL FULL TESTS (TEST_MODE=slow)")
        results["postgres"] = run_tests("slow", args.path, not args.quiet)
    
    # Print summary
    print("\n" + "="*60)
    print("TEST EXECUTION SUMMARY")
    print("="*60)
    
    for mode, success in results.items():
        status = "PASSED" if success else "FAILED"
        print(f"  {mode.upper()}: {status}")
    
    if all(results.values()):
        print("\nALL TESTS PASSED!")
        sys.exit(0)
    else:
        print("\nSOME TESTS FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()