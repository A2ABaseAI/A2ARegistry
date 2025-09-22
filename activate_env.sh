#!/bin/bash
# Script to activate the Python 3.13 virtual environment

echo "🐍 Activating Python 3.13 virtual environment..."
source venv/bin/activate

echo "✅ Virtual environment activated!"
echo "Python version: $(python --version)"
echo "Pip version: $(pip --version)"
echo ""
echo "To deactivate, run: deactivate"
echo "To run tests: python -m pytest tests/ -v"
echo "To run the app: python -m uvicorn app.main:app --reload"
