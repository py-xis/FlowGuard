import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.health import get_health_status, get_readiness_status


def test_get_health_status():
    """Test health status function"""
    health = get_health_status()
    
    assert 'status' in health
    assert 'timestamp' in health
    assert 'model_loaded' in health
    assert 'vectorizer_loaded' in health
    assert 'model_version' in health
    
    assert health['status'] in ['healthy', 'unhealthy']
    assert isinstance(health['model_loaded'], bool)
    assert isinstance(health['vectorizer_loaded'], bool)


def test_get_readiness_status():
    """Test readiness status function"""
    readiness = get_readiness_status()
    
    assert 'ready' in readiness
    assert 'timestamp' in readiness
    assert isinstance(readiness['ready'], bool)


def test_health_status_with_models():
    """Test that health status reports correctly when models exist"""
    health = get_health_status()
    
    # If both models are loaded, status should be healthy
    if health['model_loaded'] and health['vectorizer_loaded']:
        assert health['status'] == 'healthy'
    else:
        assert health['status'] == 'unhealthy'
