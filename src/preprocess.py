import string
import nltk
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from typing import List

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)
    nltk.download('punkt_tab', quiet=True)

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

ps = PorterStemmer()


def transform_text(text: str) -> str:
    """
    Transform and preprocess text for spam classification
    
    Steps:
    1. Convert to lowercase
    2. Tokenize
    3. Remove non-alphanumeric characters
    4. Remove stopwords
    5. Remove punctuation
    6. Apply stemming
    7. Join tokens
    
    Args:
        text: Input text to transform
        
    Returns:
        Preprocessed text string
    """
    # Convert to lowercase
    text = text.lower()
    
    # Tokenize
    text_tokens: List[str] = nltk.word_tokenize(text)
    
    # Remove non-alphanumeric characters
    text_tokens = [token for token in text_tokens if token.isalnum()]
    
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    text_tokens = [token for token in text_tokens if token not in stop_words]
    
    # Remove punctuation
    text_tokens = [token for token in text_tokens if token not in string.punctuation]
    
    # Apply stemming
    text_tokens = [ps.stem(token) for token in text_tokens]
    
    # Join tokens
    return ' '.join(text_tokens)


def get_text_stats(text: str) -> dict:
    """
    Get statistics about the input text
    
    Args:
        text: Input text
        
    Returns:
        Dictionary with text statistics
    """
    return {
        "original_length": len(text),
        "word_count": len(text.split()),
        "char_count": len(text),
        "transformed_text": transform_text(text)
    }
