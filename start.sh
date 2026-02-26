#!/bin/bash
echo "Starting DocPortal..."

# Set PYTHONPATH to the current directory so modules can resolve
export PYTHONPATH=$(pwd)

# Check for virtual environment and run
if [ -f "venv/bin/python" ]; then
    ./venv/bin/python unified_doc_tool/app.py
else
    echo "Warning: 'venv' not found. Attempting to run with system python3..."
    echo "Please ensure dependencies (requirements.txt) are installed."
    python3 unified_doc_tool/app.py
fi
