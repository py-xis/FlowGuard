#!/bin/bash
# Deployment script for Jenkins

set -e  # Exit on error

echo "===== Starting Deployment Process ====="

DOCKER_IMAGE=${1:-"spam-classifier:latest"}
NAMESPACE=${2:-"spam-classifier"}

echo "Deploying image: $DOCKER_IMAGE to namespace: $NAMESPACE"

# Update Kubernetes deployment
kubectl set image deployment/spam-classifier \
    spam-classifier=$DOCKER_IMAGE \
    -n $NAMESPACE

# Wait for rollout to complete
echo "Waiting for deployment to complete..."
kubectl rollout status deployment/spam-classifier -n $NAMESPACE --timeout=5m

# Verify deployment
echo "Verifying deployment..."
kubectl get pods -n $NAMESPACE -l app=spam-classifier

echo "===== Deployment Completed Successfully ====="
