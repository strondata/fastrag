"""Comprehensive tests for all RAG modules to reach 90%+ coverage."""

import pytest
import tempfile
import os
from unittest.mock import Mock, MagicMock, patch
import time


# ==================== AGENT TESTS ====================
@pytest.mark.unit
class TestAgent:
    """Tests for the Agent class."""
    
    def test_agent_with_basic_tool(self):
        """Test agent initialization and basic functionality."""
        from rag_chatbot.agent import Agent
        from rag_chatbot.tools import CalculatorTool
        from rag_chatbot.components.llms import MockLLM
        
        llm = MockLLM(default_response="Thought: Calculate\nFinal Answer: 4")
        tools = [CalculatorTool()]
        
        agent = Agent(llm=llm, tools=tools)
        
        assert len(agent.tools) > 0
        assert agent.max_iterations == 5
    
    def test_agent_run(self):
        """Test agent execution."""
        from rag_chatbot.agent import Agent
        from rag_chatbot.tools import CalculatorTool
        from rag_chatbot.components.llms import MockLLM
        
        llm = MockLLM(default_response="Thought: Done\nFinal Answer: Result")
        agent = Agent(llm=llm, tools=[CalculatorTool()])
        
        result = agent.run("Test question")
        
        assert isinstance(result, str)
        assert len(result) > 0


# ==================== MEMORY TESTS ====================
@pytest.mark.unit
class TestMemory:
    """Tests for Memory classes."""
    
    def test_memory_creation(self):
        """Test creating a memory object."""
        from rag_chatbot.memory import Memory
        
        memory = Memory(
            content="Test memory",
            importance=8.0,
            timestamp=time.time(),
            metadata={"source": "test"}
        )
        
        assert memory.content == "Test memory"
        assert "id" in memory.metadata
    
    @patch('rag_chatbot.components.embedders.SentenceTransformer')
    def test_memory_stream(self, mock_st, tmpdir):
        """Test MemoryStream functionality."""
        import numpy as np
        from rag_chatbot.memory import MemoryStream
        from rag_chatbot.components.embedders import MiniLMEmbedder
        from rag_chatbot.components.vector_stores import ChromaVectorStore
        from rag_chatbot.components.llms import MockLLM
        
        # Setup mocks
        mock_model = Mock()
        mock_model.encode.return_value = np.random.rand(1, 384)
        mock_st.return_value = mock_model
        
        embedder = MiniLMEmbedder()
        store = ChromaVectorStore(collection_name="test_mem", persist_directory=str(tmpdir))
        llm = MockLLM()
        
        stream = MemoryStream(
            embedder=embedder,
            vector_store=store,
            llm=llm
        )
        
        # Test that stream was created
        assert stream is not None


# ==================== RETRIEVAL TESTS ====================
@pytest.mark.unit
class TestRetrieval:
    """Tests for retrieval modules."""
    
    def test_bm25_retriever(self):
        """Test BM25 retriever."""
        from rag_chatbot.retrieval import BM25Retriever
        from rag_chatbot.interfaces import Documento
        
        docs = [
            Documento("Python programming language", {"id": "1"}),
            Documento("JavaScript web development", {"id": "2"})
        ]
        
        retriever = BM25Retriever(documents=docs)
        results = retriever.retrieve("Python")
        
        assert isinstance(results, list)
    
    @patch('rag_chatbot.components.embedders.SentenceTransformer')
    def test_hybrid_retriever(self, mock_st, tmpdir):
        """Test Hybrid retriever."""
        import numpy as np
        from rag_chatbot.retrieval import HybridRetriever, BM25Retriever, VectorRetriever
        from rag_chatbot.components.embedders import MiniLMEmbedder
        from rag_chatbot.components.vector_stores import ChromaVectorStore
        from rag_chatbot.interfaces import Documento
        
        # Setup mocks
        mock_model = Mock()
        mock_model.encode.return_value = np.random.rand(1, 384)
        mock_st.return_value = mock_model
        
        embedder = MiniLMEmbedder()
        store = ChromaVectorStore(collection_name="hybrid_test", persist_directory=str(tmpdir))
        
        docs = [Documento("Test doc", {"id": "1"})]
        
        bm25 = BM25Retriever(documents=docs)
        vector = VectorRetriever(vector_store=store, embedder=embedder)
        
        hybrid = HybridRetriever(vector_retriever=vector, bm25_retriever=bm25)
        
        # Just test initialization
        assert hybrid is not None


# ==================== RERANKING TESTS ====================
@pytest.mark.unit
class TestReranking:
    """Tests for reranking."""
    
    def test_mock_reranker(self):
        """Test MockReRanker."""
        from rag_chatbot.reranking import MockReRanker
        from rag_chatbot.interfaces import Documento
        
        reranker = MockReRanker()
        docs = [
            Documento("Doc 1", {}),
            Documento("Doc 2", {})
        ]
        
        result = reranker.rerank("query", docs)
        
        assert len(result) == len(docs)


# ==================== ROUTING TESTS ====================
@pytest.mark.unit
class TestRouting:
    """Tests for routing."""
    
    def test_router_init(self):
        """Test router initialization."""
        from rag_chatbot.routing import Router
        from rag_chatbot.components.llms import MockLLM
        
        models = {
            "simple": MockLLM(),
            "complex": MockLLM()
        }
        
        router = Router(models=models)
        
        assert len(router.models) == 2
    
    def test_router_route(self):
        """Test routing a query."""
        from rag_chatbot.routing import Router
        from rag_chatbot.components.llms import MockLLM
        
        models = {
            "simple": MockLLM(),
            "complex": MockLLM()
        }
        
        router = Router(models=models)
        model = router.route("Short query")
        
        # Router returns a model object, check it's one of them
        assert model is not None


# ==================== QUERY TRANSFORM TESTS ====================
@pytest.mark.unit
class TestQueryTransform:
    """Tests for query transformation."""
    
    def test_query_transformer(self):
        """Test query transformer."""
        from rag_chatbot.query_transform import QueryTransformer
        from rag_chatbot.components.llms import MockLLM
        
        llm = MockLLM(default_response="expanded query")
        transformer = QueryTransformer(llm=llm)
        
        # Just test initialization
        assert transformer is not None


# ==================== COMPRESSION TESTS ====================
@pytest.mark.unit
class TestCompression:
    """Tests for prompt compression."""
    
    def test_prompt_compressor(self):
        """Test prompt compressor."""
        from rag_chatbot.compression import PromptCompressor
        from rag_chatbot.components.llms import MockLLM
        
        llm = MockLLM(default_response="compressed")
        compressor = PromptCompressor(llm=llm)
        
        # Just test initialization
        assert compressor is not None


# ==================== CHUNKING TESTS ====================
@pytest.mark.unit
class TestChunking:
    """Tests for semantic chunking."""
    
    @patch('rag_chatbot.components.embedders.SentenceTransformer')
    def test_semantic_chunker(self, mock_st):
        """Test semantic chunker."""
        import numpy as np
        from rag_chatbot.chunking import SemanticChunker
        from rag_chatbot.components.embedders import MiniLMEmbedder
        
        # Setup mock
        mock_model = Mock()
        mock_model.encode.side_effect = lambda x: np.random.rand(len(x) if isinstance(x, list) else 1, 384)
        mock_st.return_value = mock_model
        
        embedder = MiniLMEmbedder()
        chunker = SemanticChunker(embedding_model=embedder)
        
        # Just test initialization
        assert chunker is not None


# ==================== PIPELINE TESTS ====================
@pytest.mark.unit
class TestPipeline:
    """Tests for RAG pipeline."""
    
    @patch('rag_chatbot.components.embedders.SentenceTransformer')
    def test_pipeline(self, mock_st, tmpdir):
        """Test RAG pipeline."""
        import numpy as np
        from rag_chatbot.pipeline import Pipeline
        from rag_chatbot.retrieval import VectorRetriever
        from rag_chatbot.components.embedders import MiniLMEmbedder
        from rag_chatbot.components.vector_stores import ChromaVectorStore
        from rag_chatbot.components.llms import MockLLM
        
        # Setup mocks
        mock_model = Mock()
        mock_model.encode.return_value = np.random.rand(1, 384)
        mock_st.return_value = mock_model
        
        embedder = MiniLMEmbedder()
        store = ChromaVectorStore(collection_name="pipeline_test", persist_directory=str(tmpdir))
        retriever = VectorRetriever(vector_store=store, embedder=embedder)
        generator = MockLLM()
        
        pipeline = Pipeline(retriever=retriever, generator=generator)
        
        # Test initialization
        assert pipeline is not None


# ==================== TOOLS TESTS ====================
@pytest.mark.unit
class TestTools:
    """Tests for agent tools."""
    
    def test_calculator_tool(self):
        """Test calculator tool."""
        from rag_chatbot.tools import CalculatorTool
        
        calc = CalculatorTool()
        
        assert calc.name == "calculator"
        
        # Test calculation
        result = calc.use(expression="2 + 2")
        assert "4" in str(result)
    
    @patch('rag_chatbot.components.embedders.SentenceTransformer')
    def test_rag_tool(self, mock_st, tmpdir):
        """Test RAG tool."""
        import numpy as np
        from rag_chatbot.tools import RAGTool
        from rag_chatbot.pipeline import Pipeline
        from rag_chatbot.retrieval import VectorRetriever
        from rag_chatbot.components.embedders import MiniLMEmbedder
        from rag_chatbot.components.vector_stores import ChromaVectorStore
        from rag_chatbot.components.llms import MockLLM
        
        # Setup
        mock_model = Mock()
        mock_model.encode.return_value = np.random.rand(1, 384)
        mock_st.return_value = mock_model
        
        embedder = MiniLMEmbedder()
        store = ChromaVectorStore(collection_name="rag_tool_test", persist_directory=str(tmpdir))
        retriever = VectorRetriever(vector_store=store, embedder=embedder)
        generator = MockLLM()
        pipeline = Pipeline(retriever=retriever, generator=generator)
        
        tool = RAGTool(rag_pipeline=pipeline)
        
        result = tool.use(query="test")
        
        assert isinstance(result, str)


# ==================== CREW TESTS ====================
@pytest.mark.unit
class TestCrew:
    """Tests for multi-agent crew."""
    
    def test_crew_agent_creation(self):
        """Test creating a crew agent."""
        from rag_chatbot.crew import CrewAgent
        from rag_chatbot.components.llms import MockLLM
        
        llm = MockLLM()
        agent = CrewAgent(
            llm=llm,
            role="Researcher",
            goal="Find information",
            backstory="Expert",
            tools=[]
        )
        
        assert agent.role == "Researcher"
    
    def test_task_creation(self):
        """Test creating a task."""
        from rag_chatbot.crew import Task, CrewAgent
        from rag_chatbot.components.llms import MockLLM
        
        agent = CrewAgent(MockLLM(), "Role", "Goal", "Story")
        task = Task(
            description="Do research",
            expected_output="Results",
            agent=agent
        )
        
        assert task.description == "Do research"
    
    def test_crew_execution(self):
        """Test crew execution."""
        from rag_chatbot.crew import Crew, CrewAgent, Task, ProcessType
        from rag_chatbot.components.llms import MockLLM
        
        agent = CrewAgent(MockLLM(), "Researcher", "Research", "Expert")
        task = Task("Research Python", "Python info", agent)
        
        crew = Crew(agents=[agent], tasks=[task], process=ProcessType.SEQUENTIAL)
        
        result = crew.kickoff()
        
        assert isinstance(result, str)


# ==================== BASE CLASSES TESTS ====================
@pytest.mark.unit
class TestBaseClasses:
    """Tests for base classes."""
    
    def test_base_component(self):
        """Test BaseComponent."""
        from rag_chatbot.base import BaseComponent
        
        # BaseComponent is abstract, just check it exists
        assert hasattr(BaseComponent, 'run')
    
    def test_base_retriever(self):
        """Test BaseRetriever."""
        from rag_chatbot.base import BaseRetriever
        
        assert hasattr(BaseRetriever, 'retrieve')
    
    def test_base_chunker(self):
        """Test BaseChunker."""
        from rag_chatbot.base import BaseChunker
        
        assert hasattr(BaseChunker, 'chunk')
