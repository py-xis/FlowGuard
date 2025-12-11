import os
import pickle
from typing import Dict, Any
from datetime import datetime

def get_health_status() -> Dict[str, Any]:
    """
    Get application health status
    
    Returns:
        Dictionary containing health status information
    """
    health = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "model_loaded": False,
        "vectorizer_loaded": False,
        "model_version": os.getenv("MODEL_VERSION", "v1.0.0"),
        "git_commit": os.getenv("GIT_COMMIT", "unknown"),
        "build_number": os.getenv("BUILD_NUMBER", "unknown"),
        "pod_name": os.getenv("HOSTNAME", "unknown")
    }
    
    try:
        # Check if model files exist
        model_path = os.getenv("MODEL_PATH", "models/model.pkl")
        vectorizer_path = os.getenv("VECTORIZER_PATH", "models/vectorizer.pkl")
        
        if os.path.exists(model_path):
            health["model_loaded"] = True
        
        if os.path.exists(vectorizer_path):
            health["vectorizer_loaded"] = True
            
        # Overall health check
        if not (health["model_loaded"] and health["vectorizer_loaded"]):
            health["status"] = "unhealthy"
            health["error"] = "Model or vectorizer not loaded"
            
    except Exception as e:
        health["status"] = "unhealthy"
        health["error"] = str(e)
    
    return health


def get_readiness_status() -> Dict[str, bool]:
    """
    Get application readiness status for Kubernetes readiness probe
    
    Returns:
        Dictionary with readiness status
    """
    model_path = os.getenv("MODEL_PATH", "models/model.pkl")
    vectorizer_path = os.getenv("VECTORIZER_PATH", "models/vectorizer.pkl")
    
    ready = os.path.exists(model_path) and os.path.exists(vectorizer_path)
    
    return {
        "ready": ready,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
