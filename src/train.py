import os
import mlflow
import mlflow.sklearn
import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from src.preprocess import transform_text
from src.utils.logger import setup_logger
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

logger = setup_logger("spam_classifier.train")


def plot_confusion_matrix(cm, filename="confusion_matrix.png"):
    """Plot and save confusion matrix"""
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=['Not Spam', 'Spam'],
                yticklabels=['Not Spam', 'Spam'])
    plt.title('Confusion Matrix')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.savefig(filename)
    plt.close()
    return filename


def train_model(algorithm='naive_bayes', max_features=3000, ngram_range=(1, 2)):
    """
    Train spam classifier model with MLflow tracking
    
    Args:
        algorithm: Which algorithm to use ('naive_bayes', 'random_forest', 'svm')
        max_features: Maximum features for TF-IDF vectorizer
        ngram_range: N-gram range for TF-IDF
    """
    # Set MLflow tracking URI
    mlflow_uri = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
    mlflow.set_tracking_uri(mlflow_uri)
    
    # Create or get experiment with proper artifact location
    experiment_name = "spam-classifier-training"
    try:
        experiment = mlflow.get_experiment_by_name(experiment_name)
        if experiment is None:
            # Create experiment with local artifact location
            artifact_location = f"file://{os.path.abspath('mlruns')}"
            experiment_id = mlflow.create_experiment(experiment_name, artifact_location=artifact_location)
            logger.info(f"Created experiment with artifact location: {artifact_location}")
        else:
            experiment_id = experiment.experiment_id
    except Exception as e:
        logger.warning(f"Error managing experiment: {e}, using set_experiment instead")
        mlflow.set_experiment(experiment_name)
    
    logger.info(f"Starting training with algorithm={algorithm}")
    
    with mlflow.start_run():
        # Log parameters
        mlflow.log_param("algorithm", algorithm)
        mlflow.log_param("max_features", max_features)
        mlflow.log_param("ngram_range", str(ngram_range))
        
        # Load data
        logger.info("Loading dataset")
        df = pd.read_csv('data/spam.csv', encoding='latin-1')
        df = df[['v1', 'v2']]
        df.columns = ['label', 'text']
        
        # Log dataset stats
        mlflow.log_param("total_samples", len(df))
        mlflow.log_param("spam_count", (df['label'] == 'spam').sum())
        mlflow.log_param("ham_count", (df['label'] == 'ham').sum())
        
        # Preprocess
        logger.info("Preprocessing text")
        df['transformed_text'] = df['text'].apply(transform_text)
        
        # Encode labels
        df['label_encoded'] = df['label'].map({'ham': 0, 'spam': 1})
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            df['transformed_text'],
            df['label_encoded'],
            test_size=0.2,
            random_state=42,
            stratify=df['label_encoded']
        )
        
        mlflow.log_param("train_size", len(X_train))
        mlflow.log_param("test_size", len(X_test))
        
        # Vectorize
        logger.info("Creating TF-IDF vectorizer")
        vectorizer = TfidfVectorizer(max_features=max_features, ngram_range=ngram_range)
        X_train_vec = vectorizer.fit_transform(X_train)
        X_test_vec = vectorizer.transform(X_test)
        
        # Train model
        logger.info(f"Training {algorithm} model")
        if algorithm == 'naive_bayes':
            model = MultinomialNB()
        elif algorithm == 'random_forest':
            model = RandomForestClassifier(n_estimators=100, random_state=42)
            mlflow.log_param("n_estimators", 100)
        elif algorithm == 'svm':
            model = SVC(kernel='linear', probability=True, random_state=42)
            mlflow.log_param("kernel", "linear")
        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")
        
        model.fit(X_train_vec, y_train)
        
        # Predict
        y_pred = model.predict(X_test_vec)
        
        # Calculate metrics
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred)
        recall = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        
        # Log metrics
        logger.info(f"Model metrics - Accuracy: {accuracy:.4f}, Precision: {precision:.4f}, Recall: {recall:.4f}, F1: {f1:.4f}")
        mlflow.log_metric("accuracy", accuracy)
        mlflow.log_metric("precision", precision)
        mlflow.log_metric("recall", recall)
        mlflow.log_metric("f1_score", f1)
        
        # Confusion matrix
        cm = confusion_matrix(y_test, y_pred)
        cm_plot = plot_confusion_matrix(cm)
        mlflow.log_artifact(cm_plot)
        
        # Save model and vectorizer
        logger.info("Saving model and vectorizer")
        with open('models/model.pkl', 'wb') as f:
            pickle.dump(model, f)
        with open('models/vectorizer.pkl', 'wb') as f:
            pickle.dump(vectorizer, f)
        
        # Log model to MLflow
        mlflow.sklearn.log_model(model, "model")
        mlflow.log_artifact("models/model.pkl")
        mlflow.log_artifact("models/vectorizer.pkl")
        
        # Log dataset statistics
        stats = {
            "total_samples": len(df),
            "spam_samples": int((df['label'] == 'spam').sum()),
            "ham_samples": int((df['label'] == 'ham').sum()),
            "accuracy": float(accuracy),
            "precision": float(precision),
            "recall": float(recall),
            "f1_score": float(f1)
        }
        
        import json
        with open('training_stats.json', 'w') as f:
            json.dump(stats, f, indent=2)
        mlflow.log_artifact('training_stats.json')
        
        logger.info(f"Training completed successfully. Run ID: {mlflow.active_run().info.run_id}")
        
        return accuracy, precision, recall, f1


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Train spam classifier")
    parser.add_argument("--algorithm", default="naive_bayes", 
                       choices=["naive_bayes", "random_forest", "svm"],
                       help="Algorithm to use")
    parser.add_argument("--max-features", type=int, default=3000,
                       help="Max features for TF-IDF")
    
    args = parser.parse_args()
    
    train_model(algorithm=args.algorithm, max_features=args.max_features)
