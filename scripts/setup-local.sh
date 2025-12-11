#!/bin/bash
# Local development setup script

set -e

echo "===== Setting up Local Development Environment ====="

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Download NLTK data
echo "Downloading NLTK data..."
python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab'); nltk.download('stopwords')"

echo ""
echo "===== Setup Complete ====="
echo ""
echo "To start local development:"
echo "  1. Activate virtual environment: source venv/bin/activate"
echo "  2. Start Docker Compose: docker-compose -f docker/docker-compose.yml up"
echo "  3. Access application: http://localhost:8501"
echo "  4. Access MLflow: http://localhost:5000"
echo "  5. Access Prometheus: http://localhost:9090"
echo ""
