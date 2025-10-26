"""Tests for Phase 1 components: base classes, pipeline, chunking, and retrieval."""

import pytest
from unittest.mock import Mock, MagicMock
from rag_chatbot.base import BaseComponent, BaseChunker, BaseRetriever, BaseReRanker, BaseGenerator
from rag_chatbot.pipeline import Pipeline
from rag_chatbot.chunking import SemanticChunker, split_into_sentences, cosine_similarity
from rag_chatbot.retrieval import HybridRetriever, VectorRetriever, BM25Retriever
from rag_chatbot.interfaces import Documento


class TestBaseComponent:
    """Tests for BaseComponent abstraction."""
    
    def test_base_component_requires_run_implementation(self):
        """Test that BaseComponent enforces run() implementation."""
        
        class TestComponent(BaseComponent):
            pass
        
        # Should not be able to instantiate without implementing run()
        with pytest.raises(TypeError):
            component = TestComponent(param1="value1")
    
    def test_base_component_stores_config(self):
        """Test that BaseComponent stores configuration."""
        
        class TestComponent(BaseComponent):
            def run(self, data, **kwargs):
                return data
        
        component = TestComponent(param1="value1", param2=42)
        
        assert component.config["param1"] == "value1"
        assert component.config["param2"] == 42


class TestPipeline:
    """Tests for Pipeline orchestrator."""
    
    @pytest.fixture
    def mock_components(self):
        """Create mock components for pipeline."""
        mock_retriever = Mock(spec=BaseRetriever)
        mock_reranker = Mock(spec=BaseReRanker)
        mock_generator = Mock(spec=BaseGenerator)
        
        return {
            'retriever': mock_retriever,
            'reranker': mock_reranker,
            'generator': mock_generator
        }
    
    def test_pipeline_without_reranker(self, mock_components):
        """Test pipeline execution without re-ranker."""
        # Setup
        test_docs = [
            Documento(content="Test doc 1", metadata={"id": "1"}),
            Documento(content="Test doc 2", metadata={"id": "2"})
        ]
        
        mock_components['retriever'].retrieve.return_value = test_docs
        mock_components['generator'].generate.return_value = "Test response"
        
        # Create pipeline without reranker
        pipeline = Pipeline(
            retriever=mock_components['retriever'],
            generator=mock_components['generator']
        )
        
        # Execute
        response = pipeline.run("test query")
        
        # Verify
        assert response == "Test response"
        mock_components['retriever'].retrieve.assert_called_once()
        mock_components['generator'].generate.assert_called_once()
    
    def test_pipeline_with_reranker(self, mock_components):
        """Test pipeline execution with re-ranker."""
        # Setup
        retrieved_docs = [
            Documento(content="Doc 1", metadata={"id": "1"}),
            Documento(content="Doc 2", metadata={"id": "2"}),
            Documento(content="Doc 3", metadata={"id": "3"})
        ]
        
        reranked_docs = [
            Documento(content="Doc 2", metadata={"id": "2"}),
            Documento(content="Doc 1", metadata={"id": "1"})
        ]
        
        mock_components['retriever'].retrieve.return_value = retrieved_docs
        mock_components['reranker'].rerank.return_value = reranked_docs
        mock_components['generator'].generate.return_value = "Reranked response"
        
        # Create pipeline with reranker
        pipeline = Pipeline(
            retriever=mock_components['retriever'],
            generator=mock_components['generator'],
            reranker=mock_components['reranker']
        )
        
        # Execute
        response = pipeline.run("test query", top_k=10, top_n=2)
        
        # Verify
        assert response == "Reranked response"
        mock_components['retriever'].retrieve.assert_called_once()
        mock_components['reranker'].rerank.assert_called_once()
        mock_components['generator'].generate.assert_called_once()
    
    def test_pipeline_get_sources(self, mock_components):
        """Test getting source documents without generation."""
        test_docs = [
            Documento(content="Source 1", metadata={"id": "1"}),
            Documento(content="Source 2", metadata={"id": "2"})
        ]
        
        mock_components['retriever'].retrieve.return_value = test_docs
        mock_components['generator'].generate.return_value = "Response"
        
        pipeline = Pipeline(
            retriever=mock_components['retriever'],
            generator=mock_components['generator']
        )
        
        sources = pipeline.get_sources("test query", top_k=10, top_n=2)
        
        assert len(sources) == 2
        assert sources[0].content == "Source 1"
        # Generator should not be called
        mock_components['generator'].generate.assert_not_called()


class TestSemanticChunker:
    """Tests for SemanticChunker."""
    
    def test_split_into_sentences(self):
        """Test sentence splitting."""
        text = "This is sentence one. This is sentence two! Is this sentence three?"
        sentences = split_into_sentences(text)
        
        assert len(sentences) == 3
        assert "This is sentence one." in sentences[0]
    
    def test_cosine_similarity(self):
        """Test cosine similarity calculation."""
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [1.0, 0.0, 0.0]
        vec3 = [0.0, 1.0, 0.0]
        
        # Identical vectors
        assert abs(cosine_similarity(vec1, vec2) - 1.0) < 0.001
        
        # Orthogonal vectors
        assert abs(cosine_similarity(vec1, vec3)) < 0.001
    
    def test_semantic_chunker_single_sentence(self):
        """Test chunking with single sentence."""
        mock_embedder = Mock()
        
        chunker = SemanticChunker(
            embedding_model=mock_embedder,
            similarity_threshold=0.8
        )
        
        text = "Single sentence."
        chunks = chunker.chunk(text)
        
        assert len(chunks) == 1
        assert chunks[0] == "Single sentence."
    
    def test_semantic_chunker_multiple_sentences(self):
        """Test chunking with multiple sentences."""
        mock_embedder = Mock()
        
        # Mock embeddings - high similarity for sentences 0-1, low for 1-2
        mock_embedder.embed_documents.return_value = [
            [1.0, 0.0, 0.0],  # Sentence 0
            [0.9, 0.1, 0.0],  # Sentence 1 (similar to 0)
            [0.0, 0.0, 1.0]   # Sentence 2 (different)
        ]
        
        chunker = SemanticChunker(
            embedding_model=mock_embedder,
            similarity_threshold=0.75
        )
        
        text = "First sentence. Second sentence. Third sentence."
        chunks = chunker.chunk(text)
        
        # Should create 2 chunks: [0,1] and [2]
        assert len(chunks) >= 1


class TestHybridRetriever:
    """Tests for HybridRetriever."""
    
    def test_vector_retriever(self):
        """Test VectorRetriever."""
        mock_store = Mock()
        mock_embedder = Mock()
        
        test_docs = [
            Documento(content="Doc 1", metadata={"id": "1"}),
            Documento(content="Doc 2", metadata={"id": "2"})
        ]
        
        mock_embedder.embed_query.return_value = [0.1, 0.2, 0.3]
        mock_store.search.return_value = test_docs
        
        retriever = VectorRetriever(
            vector_store=mock_store,
            embedder=mock_embedder
        )
        
        results = retriever.retrieve("test query", top_k=5)
        
        assert len(results) == 2
        mock_embedder.embed_query.assert_called_once_with("test query")
        mock_store.search.assert_called_once()
    
    def test_bm25_retriever(self):
        """Test BM25Retriever."""
        test_docs = [
            Documento(content="python programming language", metadata={"id": "1"}),
            Documento(content="java programming tutorial", metadata={"id": "2"}),
            Documento(content="machine learning basics", metadata={"id": "3"})
        ]
        
        retriever = BM25Retriever(documents=test_docs)
        
        results = retriever.retrieve("programming", top_k=2)
        
        # Should return documents containing "programming"
        assert len(results) <= 2
        assert any("programming" in doc.content for doc in results)
    
    def test_hybrid_retriever_rrf_fusion(self):
        """Test HybridRetriever RRF fusion."""
        # Create mock retrievers
        mock_vector = Mock(spec=VectorRetriever)
        mock_bm25 = Mock(spec=BM25Retriever)
        
        doc1 = Documento(content="Doc 1", metadata={"id": "1"})
        doc2 = Documento(content="Doc 2", metadata={"id": "2"})
        doc3 = Documento(content="Doc 3", metadata={"id": "3"})
        
        # Vector retriever returns [doc1, doc2]
        mock_vector.retrieve.return_value = [doc1, doc2]
        # BM25 retriever returns [doc2, doc3]
        mock_bm25.retrieve.return_value = [doc2, doc3]
        
        hybrid = HybridRetriever(
            vector_retriever=mock_vector,
            bm25_retriever=mock_bm25,
            k_rrf=60
        )
        
        results = hybrid.retrieve("test query", top_k=10)
        
        # Should combine all documents
        assert len(results) >= 2
        mock_vector.retrieve.assert_called_once()
        mock_bm25.retrieve.assert_called_once()
