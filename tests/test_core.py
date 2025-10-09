"""
Tests for the core RAG system.
"""

import pytest
from fastrag.core import RAGSystem


def test_rag_system_initialization():
    """Test RAG system can be initialized."""
    rag = RAGSystem()
    assert rag is not None
    assert rag.config == {}


def test_rag_system_with_config():
    """Test RAG system with configuration."""
    config = {"model": "test-model"}
    rag = RAGSystem(config=config)
    assert rag.config == config


def test_add_document():
    """Test adding documents to the system."""
    rag = RAGSystem()
    rag.add_document("Test document")
    assert len(rag._documents) == 1
    assert rag._documents[0] == "Test document"


def test_retrieve():
    """Test document retrieval."""
    rag = RAGSystem()
    rag.add_document("Document 1")
    rag.add_document("Document 2")
    rag.add_document("Document 3")
    
    results = rag.retrieve("test query", top_k=2)
    assert len(results) == 2
    assert results[0] == "Document 1"
    assert results[1] == "Document 2"


def test_generate():
    """Test response generation."""
    rag = RAGSystem()
    context = ["Document 1", "Document 2"]
    response = rag.generate("test query", context)
    assert "test query" in response
    assert "2 documents" in response


def test_query_end_to_end():
    """Test end-to-end query."""
    rag = RAGSystem()
    rag.add_document("Document 1")
    rag.add_document("Document 2")
    
    response = rag.query("test query")
    assert response is not None
    assert isinstance(response, str)
