import pytest
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.predict import SpamClassifier


@pytest.fixture
def classifier():
    """Fixture to create classifier instance"""
    return SpamClassifier(
        model_path="models/model.pkl",
        vectorizer_path="models/vectorizer.pkl"
    )


def test_classifier_initialization(classifier):
    """Test that classifier initializes correctly"""
    assert classifier.model is not None
    assert classifier.vectorizer is not None
    assert classifier.model_version is not None


def test_predict_spam_message(classifier):
    """Test prediction on a clear spam message"""
    spam_text = "URGENT! You have won $1000. Click here to claim now!"
    prediction, confidence, request_id = classifier.predict(spam_text)
    
    assert prediction in ['spam', 'not_spam']
    assert 0 <= confidence <= 1
    assert len(request_id) > 0


def test_predict_ham_message(classifier):
    """Test prediction on a clear legitimate message"""
    ham_text = "Hi, I'll be there at 5pm for our meeting."
    prediction, confidence, request_id = classifier.predict(ham_text)
    
    assert prediction in ['spam', 'not_spam']
    assert 0 <= confidence <= 1
    assert len(request_id) > 0


def test_predict_empty_string(classifier):
    """Test prediction on empty string"""
    # Should not crash, should return some prediction
    prediction, confidence, request_id = classifier.predict("")
    assert prediction in ['spam', 'not_spam']


def test_get_model_info(classifier):
    """Test get_model_info method"""
    info = classifier.get_model_info()
    
    assert 'model_version' in info
    assert 'model_type' in info
    assert 'vectorizer_type' in info
    assert 'pod_name' in info


def test_predict_returns_unique_request_ids(classifier):
    """Test that each prediction gets a unique request ID"""
    text = "Test message"
    _, _, request_id1 = classifier.predict(text)
    _, _, request_id2 = classifier.predict(text)
    
    assert request_id1 != request_id2


def test_confidence_score_range(classifier):
    """Test that confidence scores are in valid range"""
    texts = [
        "Win big money now!",
        "Meeting at 3pm",
        "Free viagra pills",
        "How are you doing?"
    ]
    
    for text in texts:
        _, confidence, _ = classifier.predict(text)
        assert 0 <= confidence <= 1, f"Confidence {confidence} out of range for text: {text}"
