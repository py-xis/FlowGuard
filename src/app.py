import streamlit as st
import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.predict import SpamClassifier
from src.utils.health import get_health_status, get_readiness_status
from src.utils.logger import setup_logger

# Setup logger
logger = setup_logger("spam_classifier.app")

# Page configuration
st.set_page_config(
    page_title="Email/SMS Spam Classifier",
    page_icon="📧",
    layout="centered"
)

# Initialize classifier
@st.cache_resource
def load_classifier():
    """Load and cache the spam classifier"""
    logger.info("Loading spam classifier")
    return SpamClassifier(
        model_path=os.getenv("MODEL_PATH", "models/model.pkl"),
        vectorizer_path=os.getenv("VECTORIZER_PATH", "models/vectorizer.pkl")
    )

try:
    classifier = load_classifier()
    model_info = classifier.get_model_info()
    
    # Title and description
    st.title("📧 Email/SMS Spam Classifier")
    st.markdown("### MLOps Production System")
    st.markdown("Detect spam messages using machine learning with complete DevOps pipeline")
    
    # Show model information in sidebar
    with st.sidebar:
        st.header("📊 System Information")
        st.metric("Model Version", model_info.get("model_version", "Unknown"))
        st.metric("Pod Name", model_info.get("pod_name", "Unknown"))
        st.metric("Model Type", model_info.get("model_type", "Unknown"))
        
        # Health status
        health = get_health_status()
        status_color = "🟢" if health["status"] == "healthy" else "🔴"
        st.metric("Health Status", f"{status_color} {health['status'].upper()}")
        
        st.markdown("---")
        st.markdown("**Built with:**")
        st.markdown("- 🐳 Docker")
        st.markdown("- ☸️ Kubernetes")
        st.markdown("- 🔄 Jenkins CI/CD")
        st.markdown("- 📊 MLflow")
        st.markdown("- 🔍 ELK Stack")
        st.markdown("- 🔐 Vault")
        st.markdown("- 📈 Prometheus")
    
    # Main input area
    st.markdown("---")
    input_sms = st.text_area(
        "Enter the message to classify:",
        height=150,
        placeholder="Type or paste your message here..."
    )
    
    # Predict button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        predict_button = st.button("🔍 Classify Message", use_container_width=True)
    
    if predict_button:
        if input_sms.strip():
            with st.spinner("Analyzing message..."):
                try:
                    # Make prediction
                    prediction, confidence, request_id = classifier.predict(input_sms)
                    
                    # Display result
                    st.markdown("---")
                    st.subheader("📋 Classification Result")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if prediction == "spam":
                            st.error("### 🚫 SPAM")
                            st.markdown("This message appears to be **spam**.")
                        else:
                            st.success("### ✅ NOT SPAM")
                            st.markdown("This message appears to be **legitimate**.")
                    
                    with col2:
                        st.metric("Confidence Score", f"{confidence:.2%}")
                        st.caption(f"Request ID: `{request_id[:8]}...`")
                    
                    # Show message preview
                    with st.expander("📄 Message Preview"):
                        st.text(input_sms[:200] + ("..." if len(input_sms) > 200 else ""))
                    
                    logger.info(f"UI prediction displayed: {prediction} with confidence {confidence}")
                    
                except Exception as e:
                    st.error(f"❌ Error making prediction: {str(e)}")
                    logger.error(f"UI prediction error: {str(e)}", exc_info=True)
        else:
            st.warning("⚠️ Please enter a message to classify")
    
    # Examples section
    st.markdown("---")
    with st.expander("💡 Try Example Messages"):
        st.markdown("**Spam Example:**")
        st.code("URGENT! You have won a $1000 gift card. Click here to claim now! Limited time offer!")
        
        st.markdown("**Not Spam Example:**")
        st.code("Hi, I'll be 15 minutes late for our meeting. Traffic is terrible. See you soon!")

except Exception as e:
    st.error(f"❌ Failed to initialize application: {str(e)}")
    logger.error(f"Application initialization failed: {str(e)}", exc_info=True)
    
    st.markdown("### Troubleshooting:")
    st.markdown("- Check if model files exist in `models/` directory")
    st.markdown("- Verify model.pkl and vectorizer.pkl are present")
    st.markdown("- Check application logs for detailed errors")
