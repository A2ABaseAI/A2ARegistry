#!/bin/bash
# Start the A2A Host Orchestrator Runner

cd "$(dirname "$0")"
cd ..

# Activate virtual environment
source venv/bin/activate

# Install dependencies if needed
echo "Installing dependencies..."
pip install -r runner/requirements.txt > /dev/null 2>&1

# Start the runner
echo "Starting runner on port 8001..."
cd runner
uvicorn runner.main:app --reload --port 8001

