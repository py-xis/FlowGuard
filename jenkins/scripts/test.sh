#!/bin/bash
# Test script for Jenkins

set -e  # Exit on error

echo "===== Running Tests ====="

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run pytest with coverage
pytest tests/ \
    -v \
    --cov=src \
    --cov-report=xml \
    --cov-report=html \
    --cov-report=term \
    --junit-xml=test-results.xml

echo "===== Tests Completed Successfully ====="
echo "Coverage report generated in htmlcov/ directory"
