"""Tests for Phase 2 components: query transformation, re-ranking, and compression."""

import pytest
from unittest.mock import Mock, MagicMock
from rag_chatbot.query_transform import QueryTransformer
from rag_chatbot.reranking import CrossEncoderReRanker, MockReRanker
from rag_chatbot.compression import PromptCompressor
from rag_chatbot.interfaces import Documento


class TestQueryTransformer:
    """Tests for QueryTransformer."""
    
    @pytest.fixture
    def mock_llm(self):
        """Create a mock LLM."""
        return Mock()
    
    def test_generate_multi_queries(self, mock_llm):
        """Test multi-query generation."""
        mock_llm.generate.return_value = "What is Python?\nHow does Python work?\nPython programming basics"
        
        transformer = QueryTransformer(llm=mock_llm)
        queries = transformer.generate_multi_queries("Tell me about Python", num_variations=3)
        
        # Should include original + variations
        assert len(queries) >= 1
        assert "Tell me about Python" in queries
        mock_llm.generate.assert_called_once()
    
    def test_generate_step_back_question(self, mock_llm):
        """Test step-back question generation."""
        mock_llm.generate.return_value = "What are the fundamentals of programming languages?"
        
        transformer = QueryTransformer(llm=mock_llm)
        queries = transformer.generate_step_back_question("How do I use list comprehensions in Python?")
        
        # Should return original + step-back
        assert len(queries) == 2
        assert queries[0] == "How do I use list comprehensions in Python?"
        assert "fundamentals" in queries[1].lower()
    
    def test_generate_hypothetical_document(self, mock_llm):
        """Test HyDE document generation."""
        mock_llm.generate.return_value = "Python is a high-level programming language known for its simplicity..."
        
        transformer = QueryTransformer(llm=mock_llm)
        hyde_doc = transformer.generate_hypothetical_document("What is Python?")
        
        assert len(hyde_doc) > 0
        assert "Python" in hyde_doc
        mock_llm.generate.assert_called_once()
    
    def test_run_with_different_methods(self, mock_llm):
        """Test run() with different transformation methods."""
        mock_llm.generate.return_value = "Generated content"
        
        transformer = QueryTransformer(llm=mock_llm)
        
        # Test multi_query
        result = transformer.run("test query", method="multi_query", num_variations=2)
        assert isinstance(result, list)
        
        # Test step_back
        result = transformer.run("test query", method="step_back")
        assert isinstance(result, list)
        assert len(result) == 2
        
        # Test hyde
        result = transformer.run("test query", method="hyde")
        assert isinstance(result, str)
    
    def test_error_handling(self, mock_llm):
        """Test graceful error handling."""
        mock_llm.generate.side_effect = Exception("LLM error")
        
        transformer = QueryTransformer(llm=mock_llm)
        
        # Should return original query on error
        queries = transformer.generate_multi_queries("test query")
        assert queries == ["test query"]


class TestMockReRanker:
    """Tests for MockReRanker."""
    
    def test_mock_reranker(self):
        """Test mock re-ranker functionality."""
        docs = [
            Documento(content=f"Document {i}", metadata={"id": str(i)})
            for i in range(10)
        ]
        
        reranker = MockReRanker()
        reranked = reranker.rerank("test query", docs, top_n=3)
        
        assert len(reranked) == 3
        # Should have scores attached
        assert 'rerank_score' in reranked[0].metadata
        # Scores should be descending
        assert reranked[0].metadata['rerank_score'] >= reranked[1].metadata['rerank_score']


class TestCrossEncoderReRanker:
    """Tests for CrossEncoderReRanker (without loading actual model)."""
    
    def test_initialization(self):
        """Test re-ranker initialization."""
        reranker = CrossEncoderReRanker(model_name="cross-encoder/ms-marco-MiniLM-L-6-v2")
        
        assert reranker.model_name == "cross-encoder/ms-marco-MiniLM-L-6-v2"
        assert reranker.model is None  # Lazy loading
    
    def test_rerank_with_mock_model(self):
        """Test re-ranking with mocked model."""
        reranker = CrossEncoderReRanker()
        
        # Mock the model
        mock_model = Mock()
        mock_model.predict.return_value = [0.9, 0.7, 0.5, 0.3]
        reranker.model = mock_model
        
        docs = [
            Documento(content=f"Document {i}", metadata={"id": str(i)})
            for i in range(4)
        ]
        
        reranked = reranker.rerank("test query", docs, top_n=2)
        
        # Should return top 2
        assert len(reranked) == 2
        # Should be sorted by score
        assert reranked[0].metadata['rerank_score'] == 0.9
        assert reranked[1].metadata['rerank_score'] == 0.7
        
        mock_model.predict.assert_called_once()
    
    def test_empty_documents(self):
        """Test re-ranking with empty document list."""
        reranker = CrossEncoderReRanker()
        reranker.model = Mock()  # Prevent actual loading
        
        reranked = reranker.rerank("test query", [], top_n=5)
        
        assert len(reranked) == 0


class TestPromptCompressor:
    """Tests for PromptCompressor."""
    
    def test_heuristic_compression(self):
        """Test heuristic compression."""
        compressor = PromptCompressor(compression_ratio=0.5)
        
        original = """This is a test prompt with lots of extra whitespace.
        
        
        As I mentioned before, this contains filler phrases.
        
        QUESTION: What is the answer?"""
        
        compressed = compressor.compress_heuristic(original)
        
        # Should be shorter
        assert len(compressed) < len(original)
        # Should preserve the question
        assert "QUESTION" in compressed or "What is the answer" in compressed
    
    def test_summarization_compression(self):
        """Test summarization-based compression."""
        mock_llm = Mock()
        mock_llm.generate.return_value = "This is a compressed summary."
        
        compressor = PromptCompressor(
            summarization_llm=mock_llm,
            compression_ratio=0.3
        )
        
        original = "This is a very long prompt that needs to be compressed " * 10
        compressed = compressor.compress_by_summarization(original)
        
        assert compressed == "This is a compressed summary."
        mock_llm.generate.assert_called_once()
    
    def test_compression_without_llm_falls_back(self):
        """Test that compression without LLM falls back to heuristic."""
        compressor = PromptCompressor(compression_ratio=0.5)
        
        original = "Test prompt with content"
        compressed = compressor.compress(original, method="summarization")
        
        # Should use heuristic as fallback
        assert len(compressed) <= len(original)
    
    def test_run_method(self):
        """Test run() method with different parameters."""
        compressor = PromptCompressor(compression_ratio=0.5)
        
        original = "Test prompt content that needs compression"
        
        # Test with heuristic
        result = compressor.run(original, method="heuristic", ratio=0.6)
        assert len(result) <= len(original)
    
    def test_preserve_question_in_compression(self):
        """Test that important parts (questions) are preserved."""
        compressor = PromptCompressor(compression_ratio=0.3)
        
        original = """Here is a lot of context that might not be very important.
        It goes on and on with details that could be summarized.
        More and more content here.
        
        QUESTION: What is the specific answer I need?"""
        
        compressed = compressor.compress_heuristic(original, ratio=0.3)
        
        # Question should be preserved even with aggressive compression
        assert "What is the specific answer" in compressed or "QUESTION" in compressed
    
    def test_whitespace_removal(self):
        """Test extra whitespace removal."""
        compressor = PromptCompressor(compression_ratio=0.9)
        
        original = "Text   with    lots    of     spaces"
        compressed = compressor.compress_heuristic(original)
        
        # Multiple spaces should be reduced to single spaces
        assert "    " not in compressed
        assert "Text with lots of spaces" == compressed.strip()
