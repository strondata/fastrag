"""
Tests for utility functions.
"""

import pytest
from fastrag.utils import chunk_text, preprocess_text


def test_chunk_text():
    """Test text chunking."""
    text = "a" * 1000
    chunks = chunk_text(text, chunk_size=200, overlap=50)
    
    assert len(chunks) > 1
    assert len(chunks[0]) == 200


def test_chunk_text_short():
    """Test chunking short text."""
    text = "Short text"
    chunks = chunk_text(text, chunk_size=100)
    
    assert len(chunks) == 1
    assert chunks[0] == text


def test_preprocess_text():
    """Test text preprocessing."""
    text = "  This   is   a   test  "
    processed = preprocess_text(text)
    
    assert processed == "This is a test"


def test_preprocess_text_newlines():
    """Test preprocessing with newlines."""
    text = "This\nis\na\ntest"
    processed = preprocess_text(text)
    
    assert processed == "This is a test"
