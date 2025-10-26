"""Integration tests for RAG system."""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch
from rag_chatbot.core import RAGChatbot
from rag_chatbot.components.loaders import UniversalLoader
from rag_chatbot.components.embedders import MiniLMEmbedder
from rag_chatbot.components.vector_stores import ChromaVectorStore
from rag_chatbot.components.llms import MockLLM
from rag_chatbot.interfaces import Documento


@pytest.mark.integration
class TestRAGIntegration:
    """Integration tests for RAG system components."""
    
    @pytest.fixture
    def temp_data_dir(self):
        """Create temporary directory with test files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test file
            test_file = os.path.join(tmpdir, "test.txt")
            with open(test_file, "w") as f:
                f.write("This is a test document about Python programming.\n")
                f.write("Python is a popular programming language.")
            
            yield tmpdir
    
    @pytest.fixture
    def temp_chroma_dir(self):
        """Create temporary directory for ChromaDB."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    @patch('rag_chatbot.components.embedders.SentenceTransformer')
    def test_full_rag_pipeline_mock(self, mock_st, temp_data_dir, temp_chroma_dir):
        """Test full RAG pipeline with mocked embedder."""
        import numpy as np
        
        # Setup mocks
        mock_model = Mock()
        mock_model.encode.return_value = np.array([[0.1, 0.2, 0.3]])
        mock_st.return_value = mock_model
        
        # Create components
        loader = UniversalLoader()
        embedder = MiniLMEmbedder()
        store = ChromaVectorStore(
            collection_name="test_collection",
            persist_directory=temp_chroma_dir
        )
        llm = MockLLM(default_response="Python is a programming language.")
        
        # Create RAG chatbot
        chatbot = RAGChatbot(
            loader=loader,
            embedder=embedder,
            store=store,
            llm=llm
        )
        
        # Test ingestion
        num_docs = chatbot.ingest_data(temp_data_dir)
        assert num_docs > 0
        
        # Test querying
        response = chatbot.ask("What is Python?")
        assert isinstance(response, str)
        assert len(response) > 0
    
    def test_loader_and_store_integration(self, temp_data_dir):
        """Test loader and store work together."""
        loader = UniversalLoader()
        docs = loader.load(temp_data_dir)
        
        assert len(docs) > 0
        assert all(isinstance(doc, Documento) for doc in docs)
    
    @patch('rag_chatbot.components.embedders.SentenceTransformer')
    def test_embedder_and_store_integration(self, mock_st, temp_chroma_dir):
        """Test embedder and vector store integration."""
        import numpy as np
        
        # Setup mock
        mock_model = Mock()
        mock_model.encode.return_value = np.array([[0.1, 0.2, 0.3]])
        mock_st.return_value = mock_model
        
        embedder = MiniLMEmbedder()
        store = ChromaVectorStore(
            collection_name="test_embedder_store",
            persist_directory=temp_chroma_dir
        )
        
        # Create test documents
        docs = [Documento(content="Test doc", metadata={"source": "test"})]
        embeddings = embedder.embed_documents([doc.content for doc in docs])
        
        # Add to store
        store.add(docs, embeddings)
        
        # Search
        query_emb = embedder.embed_query("Test")
        results = store.search(query_emb, k=1)
        
        assert len(results) == 1
    
    def test_mock_llm_integration(self):
        """Test MockLLM works in integration."""
        llm = MockLLM(default_response="Test response")
        
        response = llm.generate("Any prompt")
        assert response == "Test response"
        
        # Test with images
        response = llm.generate("Prompt", images_base64=["image1"])
        assert response == "Test response"


@pytest.mark.integration
class TestComponentInteraction:
    """Test how different components interact."""
    
    def test_document_flow(self):
        """Test document flow through components."""
        # Create a document
        doc = Documento(
            content="Integration test content",
            metadata={"source": "test.txt", "id": "123"}
        )
        
        assert doc.content == "Integration test content"
        assert doc.metadata["source"] == "test.txt"
    
    @patch('rag_chatbot.components.embedders.SentenceTransformer')
    def test_batch_embedding_and_storage(self, mock_st, temp_chroma_dir):
        """Test batch operations."""
        import numpy as np
        
        # Setup mock
        mock_model = Mock()
        mock_model.encode.return_value = np.array([
            [0.1, 0.2, 0.3],
            [0.4, 0.5, 0.6],
            [0.7, 0.8, 0.9]
        ])
        mock_st.return_value = mock_model
        
        embedder = MiniLMEmbedder()
        store = ChromaVectorStore(
            collection_name="batch_test",
            persist_directory=temp_chroma_dir
        )
        
        # Create multiple documents
        docs = [
            Documento(f"Document {i}", {"id": str(i)})
            for i in range(3)
        ]
        
        # Embed and store
        embeddings = embedder.embed_documents([d.content for d in docs])
        store.add(docs, embeddings)
        
        # Verify
        query_emb = embedder.embed_query("Document")
        results = store.search(query_emb, k=3)
        
        assert len(results) == 3
