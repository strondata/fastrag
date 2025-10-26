"""Comprehensive unit tests for memory module."""

import pytest
from unittest.mock import Mock, MagicMock
import time
from rag_chatbot.memory import Memory, MemoryStream


class TestMemory:
    """Test suite for Memory class."""
    
    def test_memory_creation(self):
        """Test creating a memory."""
        memory = Memory(
            content="Test memory",
            importance=8.0,
            timestamp=time.time(),
            metadata={"source": "test"}
        )
        
        assert memory.content == "Test memory"
        assert memory.importance == 8.0
        assert "id" in memory.metadata
    
    def test_memory_auto_id_generation(self):
        """Test automatic ID generation."""
        memory1 = Memory("Content 1", 5.0, time.time(), {})
        memory2 = Memory("Content 2", 5.0, time.time(), {})
        
        assert "id" in memory1.metadata
        assert "id" in memory2.metadata
        assert memory1.metadata["id"] != memory2.metadata["id"]
    
    def test_memory_custom_id(self):
        """Test memory with custom ID."""
        custom_id = "custom_123"
        memory = Memory("Content", 5.0, time.time(), {"id": custom_id})
        
        assert memory.metadata["id"] == custom_id


class TestMemoryStream:
    """Test suite for MemoryStream."""
    
    @pytest.fixture
    def mock_embedder(self):
        """Create mock embedder."""
        embedder = Mock()
        embedder.embed_documents.return_value = [[0.1, 0.2, 0.3]]
        embedder.embed_query.return_value = [0.1, 0.2, 0.3]
        return embedder
    
    @pytest.fixture
    def mock_store(self):
        """Create mock vector store."""
        store = Mock()
        return store
    
    @pytest.fixture
    def mock_llm(self):
        """Create mock LLM."""
        llm = Mock()
        llm.generate.return_value = "8"
        return llm
    
    def test_init(self, mock_embedder, mock_store, mock_llm):
        """Test memory stream initialization."""
        stream = MemoryStream(
            embedder=mock_embedder,
            store=mock_store,
            llm=mock_llm
        )
        
        assert stream.embedder == mock_embedder
        assert stream.store == mock_store
        assert stream.llm == mock_llm
    
    def test_add_memory_simple(self, mock_embedder, mock_store, mock_llm):
        """Test adding a simple memory."""
        stream = MemoryStream(mock_embedder, mock_store, mock_llm)
        
        stream.add("Test memory content")
        
        mock_embedder.embed_documents.assert_called_once()
        mock_store.add.assert_called_once()
    
    def test_add_memory_with_importance(self, mock_embedder, mock_store, mock_llm):
        """Test adding memory with importance score."""
        stream = MemoryStream(mock_embedder, mock_store, mock_llm)
        
        stream.add("Important memory", importance=9.5)
        
        mock_store.add.assert_called_once()
    
    def test_score_importance(self, mock_embedder, mock_store, mock_llm):
        """Test importance scoring."""
        mock_llm.generate.return_value = "7"
        stream = MemoryStream(mock_embedder, mock_store, mock_llm)
        
        score = stream._score_importance("This is important")
        
        assert isinstance(score, float)
        assert 0 <= score <= 10
    
    def test_score_recency(self, mock_embedder, mock_store, mock_llm):
        """Test recency scoring."""
        stream = MemoryStream(mock_embedder, mock_store, mock_llm)
        
        recent_time = time.time()
        old_time = recent_time - 10000
        
        recent_score = stream._score_recency(recent_time)
        old_score = stream._score_recency(old_time)
        
        assert recent_score > old_score
        assert 0 <= recent_score <= 1
        assert 0 <= old_score <= 1
    
    def test_retrieve_memories(self, mock_embedder, mock_store, mock_llm):
        """Test retrieving memories."""
        from rag_chatbot.interfaces import Documento
        
        mock_store.search.return_value = [
            Documento(content="Memory 1", metadata={"importance": 8, "timestamp": time.time()}),
            Documento(content="Memory 2", metadata={"importance": 6, "timestamp": time.time() - 100})
        ]
        
        stream = MemoryStream(mock_embedder, mock_store, mock_llm)
        memories = stream.retrieve("query", k=2)
        
        assert len(memories) == 2
        mock_embedder.embed_query.assert_called_once()
        mock_store.search.assert_called_once()
    
    def test_retrieve_empty(self, mock_embedder, mock_store, mock_llm):
        """Test retrieving when no memories exist."""
        mock_store.search.return_value = []
        
        stream = MemoryStream(mock_embedder, mock_store, mock_llm)
        memories = stream.retrieve("query", k=5)
        
        assert len(memories) == 0
    
    def test_get_all_memories(self, mock_embedder, mock_store, mock_llm):
        """Test getting all memories."""
        stream = MemoryStream(mock_embedder, mock_store, mock_llm)
        stream.memories = [
            Memory("Mem 1", 5, time.time(), {}),
            Memory("Mem 2", 7, time.time(), {})
        ]
        
        all_mems = stream.get_all()
        
        assert len(all_mems) == 2
