#!/usr/bin/env python3
"""
A2A Registry API Examples Runner

This script runs all API examples in sequence and provides a comprehensive
overview of the A2A Registry API functionality.

Usage:
    python run_all_examples.py
"""

import os
import sys
import subprocess
import time
from typing import List, Dict, Any


class ExampleRunner:
    """Runner for all A2A Registry API examples."""

    def __init__(self):
        self.examples_dir = os.path.dirname(os.path.abspath(__file__))
        self.results: List[Dict[str, Any]] = []

    def run_example(self, script_name: str, description: str) -> Dict[str, Any]:
        """Run a single example script."""
        print(f"\n{'='*80}")
        print(f"RUNNING: {description}")
        print(f"Script: {script_name}")
        print(f"{'='*80}")

        script_path = os.path.join(self.examples_dir, script_name)

        if not os.path.exists(script_path):
            return {
                "script": script_name,
                "description": description,
                "status": "error",
                "message": f"Script not found: {script_path}",
                "duration": 0,
            }

        start_time = time.time()

        try:
            # Run the script
            result = subprocess.run(
                [sys.executable, script_path], capture_output=True, text=True, timeout=300  # 5 minute timeout
            )

            duration = time.time() - start_time

            if result.returncode == 0:
                return {
                    "script": script_name,
                    "description": description,
                    "status": "success",
                    "message": "Completed successfully",
                    "duration": duration,
                    "output": result.stdout,
                    "error": result.stderr,
                }
            else:
                return {
                    "script": script_name,
                    "description": description,
                    "status": "error",
                    "message": f"Script failed with return code {result.returncode}",
                    "duration": duration,
                    "output": result.stdout,
                    "error": result.stderr,
                }

        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            return {
                "script": script_name,
                "description": description,
                "status": "timeout",
                "message": "Script timed out after 5 minutes",
                "duration": duration,
            }
        except Exception as e:
            duration = time.time() - start_time
            return {
                "script": script_name,
                "description": description,
                "status": "error",
                "message": f"Unexpected error: {str(e)}",
                "duration": duration,
            }

    def run_all_examples(self):
        """Run all API examples."""
        print("A2A Registry API Examples Runner")
        print("=" * 80)

        # Define examples to run (authentication first, then others)
        examples = [
            {
                "script": "auth_api_examples.py",
                "description": "Authentication API Examples - User registration, login, and token management",
                "priority": 1,
            },
            {
                "script": "agent_api_examples.py",
                "description": "Agent API Examples - Publishing, retrieving, and managing agents",
                "priority": 2,
            },
            {
                "script": "search_api_examples.py",
                "description": "Search API Examples - Advanced search and filtering capabilities",
                "priority": 3,
            },
            {
                "script": "well_known_api_examples.py",
                "description": "Well-Known API Examples - Standard discovery endpoints",
                "priority": 4,
            },
        ]

        # Sort by priority to ensure authentication runs first
        examples.sort(key=lambda x: x["priority"])

        # Check environment
        print("\nEnvironment Check:")
        registry_url = os.getenv("A2A_REGISTRY_URL", "http://localhost:8000")
        token = os.getenv("A2A_TOKEN")
        print(f"  Registry URL: {registry_url}")
        print(f"  External Token: {'Yes' if token else 'No (will use built-in auth)'}")
        print("  Built-in Auth: Available (automatic user registration and login)")

        # Run examples
        total_start_time = time.time()

        for example in examples:
            result = self.run_example(example["script"], example["description"])
            self.results.append(result)

            # Print summary
            status_icon = "✓" if result["status"] == "success" else "✗"
            print(f"\n{status_icon} {example['description']}")
            print(f"  Status: {result['status'].upper()}")
            print(f"  Duration: {result['duration']:.2f}s")
            print(f"  Message: {result['message']}")

            if result["status"] != "success" and result.get("error"):
                print(f"  Error: {result['error'][:200]}...")

        total_duration = time.time() - total_start_time

        # Print final summary
        self.print_summary(total_duration)

    def print_summary(self, total_duration: float):
        """Print final summary of all examples."""
        print(f"\n{'='*80}")
        print("FINAL SUMMARY")
        print(f"{'='*80}")

        successful = sum(1 for r in self.results if r["status"] == "success")
        failed = sum(1 for r in self.results if r["status"] == "error")
        timed_out = sum(1 for r in self.results if r["status"] == "timeout")

        print(f"Total Examples: {len(self.results)}")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        print(f"Timed Out: {timed_out}")
        print(f"Total Duration: {total_duration:.2f}s")

        print("\nDetailed Results:")
        for result in self.results:
            status_icon = "✓" if result["status"] == "success" else "✗"
            print(f"  {status_icon} {result['script']}: {result['status']} ({result['duration']:.2f}s)")

        if failed > 0 or timed_out > 0:
            print("\nFailed Examples:")
            for result in self.results:
                if result["status"] in ["error", "timeout"]:
                    print(f"  ✗ {result['script']}: {result['message']}")
                    if result.get("error"):
                        print(f"    Error: {result['error'][:100]}...")

        print(f"\n{'='*80}")
        if successful == len(self.results):
            print("ALL EXAMPLES COMPLETED SUCCESSFULLY! 🎉")
            print("\nKey Features Demonstrated:")
            print("✓ Built-in authentication system (user registration, login, token management)")
            print("✓ Agent publishing and retrieval (public and private)")
            print("✓ Advanced search and filtering capabilities")
            print("✓ Well-known endpoint standards compliance")
            print("✓ Production-ready error handling and security")
        else:
            print("SOME EXAMPLES FAILED - CHECK OUTPUT ABOVE ⚠️")
        print(f"{'='*80}")


def main():
    """Main function."""
    runner = ExampleRunner()

    try:
        runner.run_all_examples()
    except KeyboardInterrupt:
        print("\n\nExamples interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
