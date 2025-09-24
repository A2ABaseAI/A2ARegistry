#!/usr/bin/env python3
"""
Quality Check Script for A2A Registry

This script runs comprehensive quality checks including:
- Linting (flake8)
- Security analysis (bandit)
- Type checking (mypy)
- Unit tests (pytest)

Usage:
    python quality_check.py [--lint] [--security] [--type] [--test] [--all]
    python quality_check.py --help
"""

import argparse
import subprocess
import sys
import os
from pathlib import Path
from typing import List, Tuple, Optional


class QualityChecker:
    """Quality check runner for the A2A Registry project."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.venv_path = self.project_root / "venv"
        self.python_path = self.venv_path / "bin" / "python"
        self.pip_path = self.venv_path / "bin" / "pip"
        
        # Check if virtual environment exists
        if not self.venv_path.exists():
            print("❌ Virtual environment not found. Please run 'python -m venv venv' first.")
            sys.exit(1)
    
    def run_command(self, command: List[str], description: str) -> Tuple[int, str, str]:
        """Run a command and return exit code, stdout, and stderr."""
        print(f"🔍 {description}")
        print("=" * (len(description) + 4))
        
        try:
            result = subprocess.run(
                command,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            print(f"⏰ Command timed out: {' '.join(command)}")
            return 1, "", "Command timed out"
        except Exception as e:
            print(f"❌ Error running command: {e}")
            return 1, "", str(e)
    
    def check_dependencies(self) -> bool:
        """Check if required tools are installed."""
        required_tools = ["flake8", "bandit", "mypy", "pytest"]
        missing_tools = []
        
        for tool in required_tools:
            try:
                subprocess.run(
                    [self.python_path, "-m", tool, "--version"],
                    capture_output=True,
                    check=True
                )
            except (subprocess.CalledProcessError, FileNotFoundError):
                missing_tools.append(tool)
        
        if missing_tools:
            print(f"❌ Missing required tools: {', '.join(missing_tools)}")
            print("Please install them with: pip install flake8 bandit mypy pytest")
            return False
        
        return True
    
    def run_linting(self) -> bool:
        """Run flake8 linting checks."""
        command = [
            str(self.python_path), "-m", "flake8",
            "app/", "sdk/", "tests/", "examples/",
            "--max-line-length=120",
            "--ignore=E203,W503"
        ]
        
        exit_code, stdout, stderr = self.run_command(command, "Running Linting (flake8)")
        
        if exit_code == 0:
            print("✅ Linting passed - no issues found!")
            return True
        else:
            print("⚠️  Linting issues found:")
            print(stdout)
            if stderr:
                print("Errors:")
                print(stderr)
            
            # Count issues
            issue_count = len([line for line in stdout.split('\n') if line.strip()])
            print(f"\n📊 Found {issue_count} linting issues")
            return False
    
    def run_security(self) -> bool:
        """Run bandit security analysis."""
        command = [
            str(self.python_path), "-m", "bandit",
            "-r", "app/", "sdk/",
            "-f", "json"
        ]
        
        exit_code, stdout, stderr = self.run_command(command, "Running Security Check (bandit)")
        
        if exit_code == 0:
            print("✅ Security check passed - no issues found!")
            return True
        else:
            try:
                import json
                data = json.loads(stdout)
                issue_count = len(data.get('results', []))
                
                print(f"⚠️  Security issues found: {issue_count}")
                
                # Show high/medium severity issues
                high_issues = [r for r in data.get('results', []) if r.get('issue_severity') == 'HIGH']
                medium_issues = [r for r in data.get('results', []) if r.get('issue_severity') == 'MEDIUM']
                
                if high_issues:
                    print(f"🚨 {len(high_issues)} HIGH severity issues:")
                    for issue in high_issues[:3]:  # Show first 3
                        print(f"  - {issue.get('issue_text', 'Unknown issue')}")
                
                if medium_issues:
                    print(f"⚠️  {len(medium_issues)} MEDIUM severity issues:")
                    for issue in medium_issues[:3]:  # Show first 3
                        print(f"  - {issue.get('issue_text', 'Unknown issue')}")
                
                return len(high_issues) == 0  # Pass if no high severity issues
                
            except (json.JSONDecodeError, ImportError):
                print("⚠️  Security issues found (unable to parse details)")
                print(stdout)
                return False
    
    def run_type_checking(self) -> bool:
        """Run mypy type checking."""
        command = [
            str(self.python_path), "-m", "mypy",
            "app/", "sdk/"
        ]
        
        exit_code, stdout, stderr = self.run_command(command, "Running Type Checking (mypy)")
        
        if exit_code == 0:
            print("✅ Type checking passed - no issues found!")
            return True
        else:
            print("⚠️  Type checking issues found:")
            print(stdout)
            if stderr:
                print("Errors:")
                print(stderr)
            
            # Count errors
            error_count = len([line for line in stdout.split('\n') if 'error:' in line])
            print(f"\n📊 Found {error_count} type checking issues")
            return False
    
    def run_tests(self) -> bool:
        """Run pytest unit tests."""
        # Set TEST_MODE environment variable
        env = os.environ.copy()
        env['TEST_MODE'] = 'true'
        
        command = [
            str(self.python_path), "-m", "pytest",
            "tests/",
            "--tb=line",
            "-q"
        ]
        
        exit_code, stdout, stderr = self.run_command(command, "Running Tests (pytest)")
        
        if exit_code == 0:
            print("✅ All tests passed!")
            return True
        else:
            print("❌ Some tests failed:")
            print(stdout)
            if stderr:
                print("Errors:")
                print(stderr)
            return False
    
    def run_all_checks(self) -> bool:
        """Run all quality checks."""
        print("🎯 Running Comprehensive Quality Checks")
        print("=" * 50)
        print()
        
        if not self.check_dependencies():
            return False
        
        results = {
            'linting': self.run_linting(),
            'security': self.run_security(),
            'type_checking': self.run_type_checking(),
            'tests': self.run_tests()
        }
        
        print("\n" + "=" * 50)
        print("📊 Quality Check Summary")
        print("=" * 50)
        
        passed = 0
        total = len(results)
        
        for check, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{check.replace('_', ' ').title():<20} {status}")
            if result:
                passed += 1
        
        print(f"\nOverall: {passed}/{total} checks passed")
        
        if passed == total:
            print("🎉 All quality checks passed! Code is production-ready.")
            return True
        else:
            print("⚠️  Some quality checks failed. Please review and fix issues.")
            return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run quality checks for the A2A Registry project",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python quality_check.py --all          # Run all checks
  python quality_check.py --lint         # Run only linting
  python quality_check.py --test         # Run only tests
  python quality_check.py --lint --test  # Run linting and tests
        """
    )
    
    parser.add_argument(
        '--lint', action='store_true',
        help='Run linting checks (flake8)'
    )
    parser.add_argument(
        '--security', action='store_true',
        help='Run security analysis (bandit)'
    )
    parser.add_argument(
        '--type', action='store_true',
        help='Run type checking (mypy)'
    )
    parser.add_argument(
        '--test', action='store_true',
        help='Run unit tests (pytest)'
    )
    parser.add_argument(
        '--all', action='store_true',
        help='Run all quality checks'
    )
    
    args = parser.parse_args()
    
    # If no specific checks are requested, run all
    if not any([args.lint, args.security, args.type, args.test]):
        args.all = True
    
    checker = QualityChecker()
    
    if args.all:
        success = checker.run_all_checks()
    else:
        success = True
        
        if args.lint:
            success &= checker.run_linting()
        
        if args.security:
            success &= checker.run_security()
        
        if args.type:
            success &= checker.run_type_checking()
        
        if args.test:
            success &= checker.run_tests()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
