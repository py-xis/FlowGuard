from flask import Flask, request, jsonify
import os
from src.predict import SpamClassifier
from src.utils.health import get_health_status, get_readiness_status
from src.utils.logger import setup_logger
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import time

app = Flask(__name__)
logger = setup_logger("spam_classifier.api")

# Prometheus metrics
REQUEST_COUNT = Counter('spam_classifier_requests_total', 'Total requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('spam_classifier_request_latency_seconds', 'Request latency', ['endpoint'])
PREDICTION_COUNT = Counter('spam_classifier_predictions_total', 'Total predictions', ['prediction'])

# Initialize classifier
classifier = SpamClassifier()

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint for Kubernetes liveness probe"""
    start_time = time.time()
    status = get_health_status()
    REQUEST_LATENCY.labels(endpoint='/health').observe(time.time() - start_time)
    REQUEST_COUNT.labels(method='GET', endpoint='/health', status=200).inc()
    return jsonify(status), 200 if status['status'] == 'healthy' else 503

@app.route('/ready', methods=['GET'])
def ready():
    """Readiness check endpoint for Kubernetes readiness probe"""
    start_time = time.time()
    status = get_readiness_status()
    REQUEST_LATENCY.labels(endpoint='/ready').observe(time.time() - start_time)
    REQUEST_COUNT.labels(method='GET', endpoint='/ready', status=200).inc()
    return jsonify(status), 200 if status['ready'] else 503

@app.route('/predict', methods=['POST'])
def predict():
    """Prediction endpoint"""
    start_time = time.time()
    
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            REQUEST_COUNT.labels(method='POST', endpoint='/predict', status=400).inc()
            return jsonify({'error': 'Missing text field'}), 400
        
        text = data['text']
        prediction, confidence, request_id = classifier.predict(text)
        
        # Update Prometheus metrics
        PREDICTION_COUNT.labels(prediction=prediction).inc()
        REQUEST_LATENCY.labels(endpoint='/predict').observe(time.time() - start_time)
        REQUEST_COUNT.labels(method='POST', endpoint='/predict', status=200).inc()
        
        return jsonify({
            'prediction': prediction,
            'confidence': confidence,
            'request_id': request_id,
            'model_version': classifier.model_version
        }), 200
        
    except Exception as e:
        logger.error(f"Prediction API error: {str(e)}", exc_info=True)
        REQUEST_COUNT.labels(method='POST', endpoint='/predict', status=500).inc()
        return jsonify({'error': str(e)}), 500

@app.route('/metrics', methods=['GET'])
def metrics():
    """Prometheus metrics endpoint"""
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

@app.route('/info', methods=['GET'])
def info():
    """Get model information"""
    REQUEST_COUNT.labels(method='GET', endpoint='/info', status=200).inc()
    return jsonify(classifier.get_model_info()), 200

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
