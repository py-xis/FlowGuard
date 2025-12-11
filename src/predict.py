import os
import pickle
import time
import uuid
from typing import Tuple, Dict, Any
from src.preprocess import transform_text
from src.utils.logger import setup_logger

logger = setup_logger("spam_classifier.predict")


class SpamClassifier:
    """Spam Classifier with MLflow integration and logging"""
    
    def __init__(self, model_path: str = "models/model.pkl", 
                 vectorizer_path: str = "models/vectorizer.pkl"):
        """
        Initialize spam classifier
        
        Args:
            model_path: Path to trained model pickle file
            vectorizer_path: Path to vectorizer pickle file
        """
        self.model_path = model_path
        self.vectorizer_path = vectorizer_path
        self.model = None
        self.vectorizer = None
        self.model_version = os.getenv("MODEL_VERSION", "v1.0.0")
        self.pod_name = os.getenv("HOSTNAME", "local")
        
        logger.info(f"Initializing SpamClassifier with model_version={self.model_version}")
        self.load_model()
    
    def load_model(self):
        """Load model and vectorizer from pickle files"""
        try:
            logger.info(f"Loading model from {self.model_path}")
            with open(self.model_path, 'rb') as f:
                self.model = pickle.load(f)
            
            logger.info(f"Loading vectorizer from {self.vectorizer_path}")
            with open(self.vectorizer_path, 'rb') as f:
                self.vectorizer = pickle.load(f)
            
            logger.info("Model and vectorizer loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}", exc_info=True)
            raise
    
    def predict(self, text: str) -> Tuple[str, float, str]:
        """
        Predict if text is spam or not
        
        Args:
            text: Input text to classify
            
        Returns:
            Tuple of (prediction, confidence, request_id)
        """
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        try:
            # Preprocess text
            transformed_text = transform_text(text)
            
            # Vectorize
            vector_input = self.vectorizer.transform([transformed_text])
            
            # Predict
            prediction = self.model.predict(vector_input)[0]
            
            # Get prediction probability for confidence score
            if hasattr(self.model, 'predict_proba'):
                proba = self.model.predict_proba(vector_input)[0]
                confidence = float(max(proba))
            else:
                # If model doesn't support predict_proba, use decision function or default
                if hasattr(self.model, 'decision_function'):
                    decision = self.model.decision_function(vector_input)[0]
                    confidence = float(abs(decision))
                else:
                    confidence = 1.0
            
            prediction_label = "spam" if prediction == 1 else "not_spam"
            
            # Calculate latency
            latency_ms = (time.time() - start_time) * 1000
            
            # Log prediction with extra fields
            logger.info(
                f"Prediction made: {prediction_label}",
                extra={
                    'prediction': prediction_label,
                    'confidence': confidence,
                    'model_version': self.model_version,
                    'request_id': request_id,
                    'pod_name': self.pod_name,
                    'latency_ms': latency_ms
                }
            )
            
            return prediction_label, confidence, request_id
            
        except Exception as e:
            logger.error(
                f"Prediction failed: {str(e)}",
                extra={
                    'request_id': request_id,
                    'model_version': self.model_version,
                    'pod_name': self.pod_name
                },
                exc_info=True
            )
            raise
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        return {
            "model_version": self.model_version,
            "model_type": type(self.model).__name__ if self.model else "Unknown",
            "vectorizer_type": type(self.vectorizer).__name__ if self.vectorizer else "Unknown",
            "pod_name": self.pod_name
        }
