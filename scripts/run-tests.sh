#!/bin/bash
# Run all tests with coverage

set -e

echo "===== Running Test Suite ====="

# Activate virtual environment if exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run tests
pytest tests/ -v \
    --cov=src \
    --cov-report=term \
    --cov-report=html \
    --cov-report=xml

echo ""
echo "===== Test Results ====="
echo "Coverage report: htmlcov/index.html"
echo "XML report: coverage.xml"
echo ""
