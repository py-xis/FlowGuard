#!/bin/bash
# Cleanup script

echo "===== Cleaning Up Project ====="

# Remove Python cache
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true

# Remove test artifacts
rm -rf .pytest_cache htmlcov .coverage coverage.xml test-results.xml

# Remove virtual environment
rm -rf venv

# Remove MLflow runs (local)
rm -rf mlflow/mlruns

# Remove temporary files
rm -f training_stats.json confusion_matrix.png

echo "Cleanup complete!"
