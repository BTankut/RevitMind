import os
import sys
import unittest
import json
from datetime import datetime
import subprocess
import time

def start_server():
    """Start the server in a separate process"""
    server_process = subprocess.Popen(
        [sys.executable, "server/main.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    # Wait for server to start
    time.sleep(2)
    return server_process

def stop_server(process):
    """Stop the server process"""
    process.terminate()
    process.wait()

def run_test_suite(test_module):
    """Run a test module and return results"""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(test_module)
    runner = unittest.TextTestRunner(verbosity=2)
    return runner.run(suite)

def create_summary_report(server_results, encoding_results):
    """Create a summary of all test results"""
    summary = {
        "timestamp": datetime.now().isoformat(),
        "test_suites": {
            "server_tests": {
                "total": server_results.testsRun,
                "failures": len(server_results.failures),
                "errors": len(server_results.errors),
                "success": server_results.wasSuccessful()
            },
            "encoding_tests": {
                "total": encoding_results.testsRun,
                "failures": len(encoding_results.failures),
                "errors": len(encoding_results.errors),
                "success": encoding_results.wasSuccessful()
            }
        }
    }
    
    # Add detailed failure information
    if server_results.failures or server_results.errors:
        summary["test_suites"]["server_tests"]["failure_details"] = [
            str(failure) for failure in server_results.failures + server_results.errors
        ]
    
    if encoding_results.failures or encoding_results.errors:
        summary["test_suites"]["encoding_tests"]["failure_details"] = [
            str(failure) for failure in encoding_results.failures + encoding_results.errors
        ]
    
    return summary

def main():
    # Create logs directory if it doesn't exist
    os.makedirs(os.path.join("tests", "logs"), exist_ok=True)
    
    print("Starting test suite...")
    print("\n1. Starting server for tests...")
    server_process = start_server()
    
    try:
        print("\n2. Running server tests...")
        import test_server
        server_results = run_test_suite(test_server)
        
        print("\n3. Running encoding tests...")
        import test_encoding
        encoding_results = run_test_suite(test_encoding)
        
        # Create summary report
        summary = create_summary_report(server_results, encoding_results)
        
        # Save summary report
        summary_file = os.path.join(
            "tests", 
            "logs", 
            f"test_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        print(f"\nTest summary saved to: {summary_file}")
        
        # Print summary to console
        print("\nTest Summary:")
        print("-------------")
        print(f"Server Tests: {summary['test_suites']['server_tests']['success']}")
        print(f"- Total: {summary['test_suites']['server_tests']['total']}")
        print(f"- Failures: {summary['test_suites']['server_tests']['failures']}")
        print(f"- Errors: {summary['test_suites']['server_tests']['errors']}")
        print("\nEncoding Tests: {summary['test_suites']['encoding_tests']['success']}")
        print(f"- Total: {summary['test_suites']['encoding_tests']['total']}")
        print(f"- Failures: {summary['test_suites']['encoding_tests']['failures']}")
        print(f"- Errors: {summary['test_suites']['encoding_tests']['errors']}")
        
    finally:
        print("\nStopping server...")
        stop_server(server_process)
        print("Tests completed.")

if __name__ == "__main__":
    main()
