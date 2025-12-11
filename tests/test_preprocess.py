import pytest
from src.preprocess import transform_text, get_text_stats


def test_transform_text_lowercase():
    """Test that text is converted to lowercase"""
    text = "HELLO WORLD"
    result = transform_text(text)
    assert result.islower()


def test_transform_text_removes_stopwords():
    """Test that stopwords are removed"""
    text = "This is a test message"
    result = transform_text(text)
    # 'is', 'a' are stopwords and should be removed
    assert 'is' not in result.split()
    assert 'a' not in result.split()


def test_transform_text_stemming():
    """Test that stemming is applied"""
    text = "jumping jumped jumps"
    result = transform_text(text)
    # All should be stemmed to 'jump'
    words = result.split()
    assert len(set(words)) == 1  # Should all be the same stem
    assert 'jump' in words  # Verify they stem to 'jump'


def test_transform_text_removes_punctuation():
    """Test that punctuation is removed"""
    text = "Hello, world! How are you?"
    result = transform_text(text)
    assert ',' not in result
    assert '!' not in result
    assert '?' not in result


def test_transform_text_empty_string():
    """Test handling of empty string"""
    text = ""
    result = transform_text(text)
    assert result == ""


def test_transform_text_numbers():
    """Test handling of numbers"""
    text = "Call 123-456-7890 now"
    result = transform_text(text)
    # Numbers should be present as they're alphanumeric
    assert 'call' in result or 'now' in result


def test_get_text_stats():
    """Test text statistics function"""
    text = "This is a test message"
    stats = get_text_stats(text)
    
    assert 'original_length' in stats
    assert 'word_count' in stats
    assert 'char_count' in stats
    assert 'transformed_text' in stats
    
    assert stats['original_length'] == len(text)
    assert stats['word_count'] == 5
    assert stats['char_count'] == len(text)


def test_transform_text_special_characters():
    """Test handling of special characters"""
    text = "Win $1000 NOW!!! Click here >>> www.spam.com"
    result = transform_text(text)
    # Should have text but no special chars
    assert len(result) > 0
    assert '$' not in result
    assert '>' not in result
