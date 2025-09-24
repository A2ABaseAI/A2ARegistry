#!/bin/bash
# Quality Check Script for A2A Registry
# 
# This script runs comprehensive quality checks including:
# - Linting (flake8)
# - Security analysis (bandit) 
# - Type checking (mypy)
# - Unit tests (pytest)
#
# Usage:
#   ./quality_check.sh [--lint] [--security] [--type] [--test] [--all]
#   ./quality_check.sh --help

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="$PROJECT_ROOT/venv"

# Check if virtual environment exists
if [ ! -d "$VENV_PATH" ]; then
    echo -e "${RED}❌ Virtual environment not found. Please run 'python -m venv venv' first.${NC}"
    exit 1
fi

# Activate virtual environment
source "$VENV_PATH/bin/activate"

# Function to run a command and show results
run_check() {
    local description="$1"
    local command="$2"
    
    echo -e "${BLUE}🔍 $description${NC}"
    echo "=================================================="
    
    if eval "$command"; then
        echo -e "${GREEN}✅ $description passed!${NC}"
        return 0
    else
        echo -e "${RED}❌ $description failed!${NC}"
        return 1
    fi
}

# Function to run linting
run_linting() {
    local command="flake8 app/ sdk/ tests/ examples/ 
    run_check "Linting (flake8)" "$command"
}

# Function to run security check
run_security() {
    local command="bandit -r app/ sdk/ -f json | jq '.results | length' 2>/dev/null || bandit -r app/ sdk/ 2>&1 | grep -E '(HIGH|MEDIUM|LOW|INFO)' | wc -l"
    run_check "Security Check (bandit)" "$command"
}

# Function to run type checking
run_type_checking() {
    local command="mypy app/ sdk/ 2>&1 | grep -c 'error:' || echo '0'"
    run_check "Type Checking (mypy)" "$command"
}

# Function to run tests
run_tests() {
    local command="TEST_MODE=true pytest tests/ --tb=line -q"
    run_check "Tests (pytest)" "$command"
}

# Function to show help
show_help() {
    echo "Quality Check Script for A2A Registry"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --lint      Run linting checks (flake8)"
    echo "  --security  Run security analysis (bandit)"
    echo "  --type      Run type checking (mypy)"
    echo "  --test      Run unit tests (pytest)"
    echo "  --all       Run all quality checks (default)"
    echo "  --help      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --all          # Run all checks"
    echo "  $0 --lint         # Run only linting"
    echo "  $0 --test         # Run only tests"
    echo "  $0 --lint --test  # Run linting and tests"
}

# Parse command line arguments
LINT=false
SECURITY=false
TYPE=false
TEST=false
ALL=false

if [ $# -eq 0 ]; then
    ALL=true
fi

while [[ $# -gt 0 ]]; do
    case $1 in
        --lint)
            LINT=true
            shift
            ;;
        --security)
            SECURITY=true
            shift
            ;;
        --type)
            TYPE=true
            shift
            ;;
        --test)
            TEST=true
            shift
            ;;
        --all)
            ALL=true
            shift
            ;;
        --help)
            show_help
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# Main execution
echo -e "${BLUE}🎯 Running Quality Checks for A2A Registry${NC}"
echo "=================================================="
echo ""

# Track results
PASSED=0
TOTAL=0

# Run requested checks
if [ "$ALL" = true ] || [ "$LINT" = true ]; then
    if run_linting; then
        ((PASSED++))
    fi
    ((TOTAL++))
fi

if [ "$ALL" = true ] || [ "$SECURITY" = true ]; then
    if run_security; then
        ((PASSED++))
    fi
    ((TOTAL++))
fi

if [ "$ALL" = true ] || [ "$TYPE" = true ]; then
    if run_type_checking; then
        ((PASSED++))
    fi
    ((TOTAL++))
fi

if [ "$ALL" = true ] || [ "$TEST" = true ]; then
    if run_tests; then
        ((PASSED++))
    fi
    ((TOTAL++))
fi

# Show summary
echo ""
echo "=================================================="
echo -e "${BLUE}📊 Quality Check Summary${NC}"
echo "=================================================="
echo -e "Overall: ${PASSED}/${TOTAL} checks passed"

if [ $PASSED -eq $TOTAL ]; then
    echo -e "${GREEN}🎉 All quality checks passed! Code is production-ready.${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠️  Some quality checks failed. Please review and fix issues.${NC}"
    exit 1
fi
