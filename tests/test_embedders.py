"""Comprehensive unit tests for embedders."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.rag_chatbot.components.embedders import MiniLMEmbedder


class TestMiniLMEmbedder:
    """Test suite for MiniLMEmbedder."""
    
    @pytest.fixture
    def mock_sentence_transformer(self):
        """Mock SentenceTransformer to avoid loading actual model."""
        with patch('src.rag_chatbot.components.embedders.SentenceTransformer') as mock:
            mock_instance = MagicMock()
            mock.return_value = mock_instance
            yield mock_instance
    
    def test_init_default_model(self, mock_sentence_transformer):
        """Test initialization with default model."""
        embedder = MiniLMEmbedder()
        assert embedder.model is not None
    
    def test_init_custom_model(self, mock_sentence_transformer):
        """Test initialization with custom model name."""
        custom_model = "paraphrase-multilingual-MiniLM-L12-v2"
        embedder = MiniLMEmbedder(model_name=custom_model)
        assert embedder.model is not None
    
    def test_embed_documents(self, mock_sentence_transformer):
        """Test embedding multiple documents."""
        # Setup mock - encode returns numpy array-like object with tolist()
        import numpy as np
        mock_sentence_transformer.encode.return_value = np.array([
            [0.1, 0.2, 0.3],
            [0.4, 0.5, 0.6]
        ])
        
        embedder = MiniLMEmbedder()
        texts = ["Document 1", "Document 2"]
        
        result = embedder.embed_documents(texts)
        
        # Verify encode was called
        mock_sentence_transformer.encode.assert_called_once_with(texts)
        assert result == [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
    
    def test_embed_documents_empty_list(self, mock_sentence_transformer):
        """Test embedding empty list."""
        import numpy as np
        mock_sentence_transformer.encode.return_value = np.array([])
        
        embedder = MiniLMEmbedder()
        result = embedder.embed_documents([])
        
        assert len(result) == 0
    
    def test_embed_query(self, mock_sentence_transformer):
        """Test embedding a single query."""
        import numpy as np
        mock_sentence_transformer.encode.return_value = np.array([[0.1, 0.2, 0.3]])
        
        embedder = MiniLMEmbedder()
        query = "What is the answer?"
        
        result = embedder.embed_query(query)
        
        mock_sentence_transformer.encode.assert_called_once_with([query])
        assert result == [0.1, 0.2, 0.3]
    
    def test_embed_query_special_characters(self, mock_sentence_transformer):
        """Test embedding query with special characters."""
        import numpy as np
        mock_sentence_transformer.encode.return_value = np.array([[0.7, 0.8, 0.9]])
        
        embedder = MiniLMEmbedder()
        query = "What's the 'best' solution? #AI"
        
        result = embedder.embed_query(query)
        
        assert result == [0.7, 0.8, 0.9]
    
    def test_embed_documents_unicode(self, mock_sentence_transformer):
        """Test embedding documents with Unicode characters."""
        import numpy as np
        mock_sentence_transformer.encode.return_value = np.array([
            [0.1, 0.2],
            [0.3, 0.4]
        ])
        
        embedder = MiniLMEmbedder()
        texts = ["Olá mundo! 🌍", "Привет мир"]
        
        result = embedder.embed_documents(texts)
        
        assert len(result) == 2
