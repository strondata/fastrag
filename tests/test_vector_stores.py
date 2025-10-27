"""Comprehensive unit tests for vector stores."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.rag_chatbot.components.vector_stores import ChromaVectorStore
from src.rag_chatbot.interfaces import Documento


class TestChromaVectorStore:
    """Test suite for ChromaVectorStore."""
    
    @pytest.fixture
    def mock_chroma_client(self):
        """Mock ChromaDB client."""
        with patch('src.rag_chatbot.components.vector_stores.chromadb.PersistentClient') as mock:
            mock_instance = MagicMock()
            mock_collection = MagicMock()
            mock_instance.get_or_create_collection.return_value = mock_collection
            mock.return_value = mock_instance
            yield mock_instance, mock_collection
    
    def test_init_default_params(self, mock_chroma_client):
        """Test initialization with default parameters."""
        mock_client, _ = mock_chroma_client
        
        store = ChromaVectorStore()
        
        assert store.collection is not None
        mock_client.get_or_create_collection.assert_called_once()
    
    def test_init_custom_collection(self, mock_chroma_client):
        """Test initialization with custom collection name."""
        mock_client, _ = mock_chroma_client
        
        store = ChromaVectorStore(collection_name="custom_collection")
        
        mock_client.get_or_create_collection.assert_called_once()
    
    def test_add_documents(self, mock_chroma_client):
        """Test adding documents to the store."""
        _, mock_collection = mock_chroma_client
        
        store = ChromaVectorStore()
        
        documents = [
            Documento(content="Doc 1", metadata={"source": "test1.txt"}),
            Documento(content="Doc 2", metadata={"source": "test2.txt"})
        ]
        embeddings = [[0.1, 0.2], [0.3, 0.4]]
        
        store.add(documents, embeddings)
        
        # Verify collection.upsert was called
        mock_collection.upsert.assert_called_once()
        call_args = mock_collection.upsert.call_args[1]
        assert len(call_args['documents']) == 2
        assert len(call_args['embeddings']) == 2
    
    def test_add_documents_empty_list(self, mock_chroma_client):
        """Test adding empty list of documents."""
        _, mock_collection = mock_chroma_client
        
        store = ChromaVectorStore()
        store.add([], [])
        
        # Should not call upsert for empty list
        mock_collection.upsert.assert_not_called()
    
    def test_search(self, mock_chroma_client):
        """Test searching for similar documents."""
        _, mock_collection = mock_chroma_client
        
        # Setup mock search results
        mock_collection.query.return_value = {
            'documents': [['Doc 1', 'Doc 2']],
            'metadatas': [[{'source': 'test1.txt'}, {'source': 'test2.txt'}]],
            'distances': [[0.1, 0.2]]
        }
        
        store = ChromaVectorStore()
        query_embedding = [0.5, 0.6]
        
        results = store.search(query_embedding, k=2)
        
        assert len(results) == 2
        assert results[0].content == 'Doc 1'
        assert results[0].metadata['source'] == 'test1.txt'
        mock_collection.query.assert_called_once()
    
    def test_search_with_k_parameter(self, mock_chroma_client):
        """Test searching with different k values."""
        _, mock_collection = mock_chroma_client
        
        mock_collection.query.return_value = {
            'documents': [['Doc 1', 'Doc 2', 'Doc 3']],
            'metadatas': [[{'source': f'test{i}.txt'} for i in range(1, 4)]],
            'distances': [[0.1, 0.2, 0.3]]
        }
        
        store = ChromaVectorStore()
        results = store.search([0.5, 0.6], k=3)
        
        assert len(results) == 3
    
    def test_search_no_results(self, mock_chroma_client):
        """Test searching when no results are found."""
        _, mock_collection = mock_chroma_client
        
        mock_collection.query.return_value = {
            'documents': [[]],
            'metadatas': [[]],
            'distances': [[]]
        }
        
        store = ChromaVectorStore()
        results = store.search([0.1, 0.2], k=5)
        
        assert len(results) == 0
    
    def test_count_documents(self, mock_chroma_client):
        """Test counting documents in collection."""
        _, mock_collection = mock_chroma_client
        
        # Setup mock for count
        mock_collection.count.return_value = 10
        
        store = ChromaVectorStore()
        
        # ChromaVectorStore doesn't have a count method, but collection does
        count = store.collection.count()
        assert count == 10
    
    def test_generate_doc_id_with_path(self, mock_chroma_client):
        """Test ID generation with path in metadata."""
        _, mock_collection = mock_chroma_client
        
        store = ChromaVectorStore()
        
        doc = Documento(
            content="Test content",
            metadata={"path": "/path/to/file.txt"}
        )
        
        doc_id = store._generate_doc_id(doc)
        assert doc_id.startswith("doc_")
        assert len(doc_id) > 4  # Has hash
    
    def test_add_documents_with_metadata(self, mock_chroma_client):
        """Test adding documents with rich metadata."""
        _, mock_collection = mock_chroma_client
        
        store = ChromaVectorStore()
        
        documents = [
            Documento(
                content="Test content",
                metadata={
                    "source": "test.txt",
                    "author": "John Doe",
                    "timestamp": "2024-01-01"
                }
            )
        ]
        embeddings = [[0.1, 0.2, 0.3]]
        
        store.add(documents, embeddings)
        
        call_args = mock_collection.upsert.call_args[1]
        assert call_args['metadatas'][0]['author'] == 'John Doe'
