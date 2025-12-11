#!/bin/bash
# Build script for Jenkins

set -e  # Exit on error

echo "===== Starting Build Process ====="
echo "Build Number: ${BUILD_NUMBER:-local}"
echo "Git Commit: $(git rev-parse --short HEAD)"

# Build Docker image
echo "Building Docker image..."
docker build \
    -f docker/Dockerfile \
    -t spam-classifier:${BUILD_NUMBER:-latest} \
    .

echo "===== Build Completed Successfully ====="
