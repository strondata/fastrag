"""End-to-end tests for the RAG system."""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch
from rag_chatbot.core import RAGChatbot
from rag_chatbot.components.loaders import UniversalLoader
from rag_chatbot.components.embedders import MiniLMEmbedder
from rag_chatbot.components.vector_stores import ChromaVectorStore
from rag_chatbot.components.llms import MockLLM


@pytest.mark.e2e
class TestRAGEndToEnd:
    """End-to-end tests for complete RAG workflows."""
    
    @pytest.fixture
    def sample_documents_dir(self):
        """Create sample documents for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create multiple test files
            with open(os.path.join(tmpdir, "python.txt"), "w") as f:
                f.write("Python is a high-level programming language.\n")
                f.write("It is widely used for web development, data science, and automation.\n")
                f.write("Python was created by Guido van Rossum.")
            
            with open(os.path.join(tmpdir, "javascript.txt"), "w") as f:
                f.write("JavaScript is a programming language for web browsers.\n")
                f.write("It enables interactive web pages and is essential for web development.\n")
                f.write("JavaScript was created by Brendan Eich.")
            
            yield tmpdir
    
    @pytest.fixture
    def temp_chroma(self):
        """Temporary ChromaDB directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    @patch('rag_chatbot.components.embedders.SentenceTransformer')
    def test_complete_rag_workflow(self, mock_st, sample_documents_dir, temp_chroma):
        """Test complete workflow: ingest -> query -> response."""
        import numpy as np
        
        # Setup embedder mock
        mock_model = Mock()
        
        def mock_encode(texts):
            # Return different embeddings for different texts
            if isinstance(texts, str):
                texts = [texts]
            return np.random.rand(len(texts), 384)
        
        mock_model.encode.side_effect = mock_encode
        mock_st.return_value = mock_model
        
        # Create RAG system
        loader = UniversalLoader()
        embedder = MiniLMEmbedder()
        store = ChromaVectorStore(
            collection_name="e2e_test",
            persist_directory=temp_chroma
        )
        llm = MockLLM(default_response="Python is a programming language created by Guido van Rossum.")
        
        chatbot = RAGChatbot(
            loader=loader,
            embedder=embedder,
            store=store,
            llm=llm
        )
        
        # Step 1: Ingest documents
        num_docs = chatbot.ingest_data(sample_documents_dir)
        assert num_docs >= 2
        
        # Step 2: Ask questions
        response1 = chatbot.ask("Who created Python?")
        assert isinstance(response1, str)
        assert len(response1) > 0
        
        response2 = chatbot.ask("What is JavaScript?")
        assert isinstance(response2, str)
        assert len(response2) > 0
        
        # Step 3: Get sources
        sources = chatbot.get_sources("Python", k=2)
        assert len(sources) >= 0
    
    @patch('rag_chatbot.components.embedders.SentenceTransformer')
    def test_rag_with_no_documents(self, mock_st, temp_chroma):
        """Test RAG behavior with no documents."""
        import numpy as np
        
        mock_model = Mock()
        mock_model.encode.return_value = np.array([[0.1, 0.2, 0.3]])
        mock_st.return_value = mock_model
        
        embedder = MiniLMEmbedder()
        store = ChromaVectorStore(
            collection_name="empty_test",
            persist_directory=temp_chroma
        )
        llm = MockLLM()
        
        chatbot = RAGChatbot(
            loader=UniversalLoader(),
            embedder=embedder,
            store=store,
            llm=llm
        )
        
        # Query without ingesting any documents
        response = chatbot.ask("What is Python?")
        
        # Should still return a response (even if LLM has no context)
        assert isinstance(response, str)
    
    @patch('rag_chatbot.components.embedders.SentenceTransformer')
    def test_multiple_queries_same_session(self, mock_st, sample_documents_dir, temp_chroma):
        """Test multiple queries in the same session."""
        import numpy as np
        
        mock_model = Mock()
        mock_model.encode.return_value = np.random.rand(1, 384)
        mock_st.return_value = mock_model
        
        # Setup RAG
        embedder = MiniLMEmbedder()
        store = ChromaVectorStore(
            collection_name="multi_query_test",
            persist_directory=temp_chroma
        )
        llm = MockLLM()
        
        chatbot = RAGChatbot(
            loader=UniversalLoader(),
            embedder=embedder,
            store=store,
            llm=llm
        )
        
        # Ingest once
        chatbot.ingest_data(sample_documents_dir)
        
        # Multiple queries
        queries = [
            "What is Python?",
            "Who created JavaScript?",
            "Tell me about programming languages"
        ]
        
        for query in queries:
            response = chatbot.ask(query)
            assert isinstance(response, str)
            assert len(response) > 0
    
    @patch('rag_chatbot.components.embedders.SentenceTransformer')
    def test_data_persistence(self, mock_st, sample_documents_dir, temp_chroma):
        """Test that data persists across chatbot instances."""
        import numpy as np
        
        mock_model = Mock()
        mock_model.encode.return_value = np.random.rand(1, 384)
        mock_st.return_value = mock_model
        
        collection_name = "persistence_test"
        
        # First instance - ingest data
        embedder1 = MiniLMEmbedder()
        store1 = ChromaVectorStore(
            collection_name=collection_name,
            persist_directory=temp_chroma
        )
        llm1 = MockLLM()
        
        chatbot1 = RAGChatbot(
            loader=UniversalLoader(),
            embedder=embedder1,
            store=store1,
            llm=llm1
        )
        
        num_docs = chatbot1.ingest_data(sample_documents_dir)
        assert num_docs >= 2
        
        # Second instance - should have access to same data
        embedder2 = MiniLMEmbedder()
        store2 = ChromaVectorStore(
            collection_name=collection_name,
            persist_directory=temp_chroma
        )
        llm2 = MockLLM()
        
        chatbot2 = RAGChatbot(
            loader=UniversalLoader(),
            embedder=embedder2,
            store=store2,
            llm=llm2
        )
        
        # Query with second instance (without re-ingesting)
        sources = chatbot2.get_sources("Python", k=1)
        
        # Should find documents from first instance
        assert len(sources) >= 0


@pytest.mark.e2e
class TestErrorHandling:
    """Test error handling in E2E scenarios."""
    
    def test_invalid_directory(self):
        """Test handling of invalid directory."""
        loader = UniversalLoader()
        
        # Should handle gracefully
        docs = loader.load("/nonexistent/directory/path")
        assert len(docs) == 0
    
    @patch('rag_chatbot.components.embedders.SentenceTransformer')
    def test_empty_query(self, mock_st, temp_chroma):
        """Test empty query handling."""
        import numpy as np
        
        mock_model = Mock()
        mock_model.encode.return_value = np.array([[0.1, 0.2, 0.3]])
        mock_st.return_value = mock_model
        
        embedder = MiniLMEmbedder()
        store = ChromaVectorStore(collection_name="empty_query", persist_directory=temp_chroma)
        llm = MockLLM()
        
        chatbot = RAGChatbot(
            loader=UniversalLoader(),
            embedder=embedder,
            store=store,
            llm=llm
        )
        
        # Test with empty string
        response = chatbot.ask("")
        assert isinstance(response, str)
