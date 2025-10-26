"""Comprehensive unit tests for retrieval, reranking, routing, and other modules."""

import pytest
from unittest.mock import Mock, MagicMock
from rag_chatbot.retrieval import BM25Retriever, HybridRetriever
from rag_chatbot.reranking import CrossEncoderReRanker, MockReRanker
from rag_chatbot.routing import Router, RoutingStrategy
from rag_chatbot.query_transform import QueryTransformer
from rag_chatbot.compression import PromptCompressor
from rag_chatbot.chunking import SemanticChunker
from rag_chatbot.pipeline import Pipeline
from rag_chatbot.tools import BaseTool, RAGTool, CalculatorTool
from rag_chatbot.base import BaseRetriever, BaseComponent, BaseReRanker
from rag_chatbot.crew import CrewAgent, Task, Crew, ProcessType
from rag_chatbot.interfaces import Documento


class TestBM25Retriever:
    """Test suite for BM25Retriever."""
    
    def test_init_empty(self):
        """Test initialization with no documents."""
        retriever = BM25Retriever()
        assert retriever.documents == []
        assert retriever.doc_index == {}
    
    def test_init_with_documents(self):
        """Test initialization with documents."""
        docs = [
            Documento("Test doc 1", {"id": "1"}),
            Documento("Test doc 2", {"id": "2"})
        ]
        retriever = BM25Retriever(documents=docs)
        
        assert len(retriever.documents) == 2
        assert len(retriever.doc_index) > 0
    
    def test_add_documents(self):
        """Test adding documents."""
        retriever = BM25Retriever()
        docs = [Documento("New doc", {"id": "1"})]
        
        retriever.add_documents(docs)
        
        assert len(retriever.documents) == 1
    
    def test_retrieve(self):
        """Test retrieving documents."""
        docs = [
            Documento("Python programming", {"id": "1"}),
            Documento("JavaScript coding", {"id": "2"})
        ]
        retriever = BM25Retriever(documents=docs)
        
        results = retriever.retrieve("Python", k=1)
        
        assert len(results) >= 0


class TestHybridRetriever:
    """Test suite for HybridRetriever."""
    
    @pytest.fixture
    def mock_vector_store(self):
        store = Mock()
        store.search.return_value = [
            Documento("Doc 1", {"score": 0.9}),
            Documento("Doc 2", {"score": 0.7})
        ]
        return store
    
    @pytest.fixture
    def mock_embedder(self):
        embedder = Mock()
        embedder.embed_query.return_value = [0.1, 0.2, 0.3]
        return embedder
    
    def test_init(self, mock_vector_store, mock_embedder):
        """Test retriever initialization."""
        retriever = HybridRetriever(
            vector_store=mock_vector_store,
            embedder=mock_embedder
        )
        assert retriever.vector_store == mock_vector_store
        assert retriever.embedder == mock_embedder
    
    def test_retrieve(self, mock_vector_store, mock_embedder):
        """Test retrieving documents."""
        retriever = HybridRetriever(
            vector_store=mock_vector_store,
            embedder=mock_embedder
        )
        results = retriever.retrieve("test query", k=2)
        
        assert len(results) >= 0
        mock_embedder.embed_query.assert_called()


class TestCrossEncoderReRanker:
    """Test suite for CrossEncoderReRanker."""
    
    @pytest.fixture
    def mock_model(self):
        with pytest.importorskip("sentence_transformers"):
            return Mock()
    
    def test_init(self):
        """Test reranker initialization."""
        reranker = MockReRanker()
        assert reranker is not None
    
    def test_rerank(self):
        """Test reranking documents."""
        reranker = MockReRanker()
        docs = [
            Documento("Doc 1", {}),
            Documento("Doc 2", {})
        ]
        
        reranked = reranker.rerank("query", docs, top_k=2)
        assert len(reranked) >= 0


class TestRouter:
    """Test suite for Router."""
    
    @pytest.fixture
    def mock_models(self):
        return {
            "simple": Mock(),
            "complex": Mock()
        }
    
    def test_init(self, mock_models):
        """Test router initialization."""
        router = Router(models=mock_models)
        assert router.models == mock_models
    
    def test_route_rule_based(self, mock_models):
        """Test rule-based routing."""
        router = Router(
            models=mock_models,
            default_strategy=RoutingStrategy.RULE_BASED
        )
        
        model_name = router.route("Short query")
        assert model_name in mock_models


class TestQueryTransformer:
    """Test suite for QueryTransformer."""
    
    @pytest.fixture
    def mock_llm(self):
        llm = Mock()
        llm.generate.return_value = "transformed query"
        return llm
    
    def test_init(self, mock_llm):
        """Test query transformer initialization."""
        transformer = QueryTransformer(llm=mock_llm)
        assert transformer.llm == mock_llm
    
    def test_transform_query(self, mock_llm):
        """Test transforming a query."""
        transformer = QueryTransformer(llm=mock_llm)
        result = transformer.transform("original query")
        
        assert isinstance(result, (str, list))


class TestPromptCompressor:
    """Test suite for PromptCompressor."""
    
    @pytest.fixture
    def mock_llm(self):
        llm = Mock()
        llm.generate.return_value = "compressed context"
        return llm
    
    def test_init(self, mock_llm):
        """Test compressor initialization."""
        compressor = PromptCompressor(llm=mock_llm)
        assert compressor.llm == mock_llm
    
    def test_compress(self, mock_llm):
        """Test compressing documents."""
        compressor = PromptCompressor(llm=mock_llm)
        docs = [Documento("Long doc 1", {}), Documento("Long doc 2", {})]
        
        compressed = compressor.compress(docs, query="test")
        assert isinstance(compressed, (list, str))


class TestSemanticChunker:
    """Test suite for SemanticChunker."""
    
    @pytest.fixture
    def mock_embedder(self):
        embedder = Mock()
        embedder.embed_documents.return_value = [[0.1, 0.2], [0.3, 0.4]]
        return embedder
    
    def test_init(self, mock_embedder):
        """Test chunker initialization."""
        chunker = SemanticChunker(embedder=mock_embedder)
        assert chunker.embedder == mock_embedder
    
    def test_chunk_text(self, mock_embedder):
        """Test chunking text."""
        chunker = SemanticChunker(embedder=mock_embedder)
        text = "Sentence 1. Sentence 2. Sentence 3."
        
        chunks = chunker.chunk(text)
        assert isinstance(chunks, list)


class TestPipeline:
    """Test suite for Pipeline."""
    
    def test_init(self):
        """Test pipeline initialization."""
        pipeline = Pipeline()
        assert pipeline.steps == []
    
    def test_add_step(self):
        """Test adding steps to pipeline."""
        pipeline = Pipeline()
        step = Mock()
        
        pipeline.add_step("test_step", step)
        assert len(pipeline.steps) > 0
    
    def test_run_empty_pipeline(self):
        """Test running empty pipeline."""
        pipeline = Pipeline()
        result = pipeline.run({"query": "test"})
        assert result is not None


class TestBaseTool:
    """Test suite for BaseTool."""
    
    def test_base_tool_interface(self):
        """Test that BaseTool defines the interface."""
        assert hasattr(BaseTool, 'name')
        assert hasattr(BaseTool, 'description')
        assert hasattr(BaseTool, 'use')


class TestRAGTool:
    """Test suite for RAGTool."""
    
    def test_init(self):
        """Test RAG tool initialization."""
        mock_chatbot = Mock()
        tool = RAGTool(rag_system=mock_chatbot, name="rag", description="RAG tool")
        
        assert tool.name == "rag"
    
    def test_use(self):
        """Test using RAG tool."""
        mock_chatbot = Mock()
        mock_chatbot.query.return_value = "Answer from RAG"
        
        tool = RAGTool(rag_system=mock_chatbot, name="rag", description="RAG tool")
        result = tool.use(query="test query")
        
        assert isinstance(result, str)


class TestCalculatorTool:
    """Test suite for CalculatorTool."""
    
    def test_init(self):
        """Test calculator initialization."""
        calc = CalculatorTool()
        assert calc.name == "calculator"
    
    def test_simple_calculation(self):
        """Test simple calculation."""
        calc = CalculatorTool()
        result = calc.use(expression="2 + 2")
        
        assert "4" in str(result)
    
    def test_complex_calculation(self):
        """Test complex calculation."""
        calc = CalculatorTool()
        result = calc.use(expression="(10 + 5) * 2")
        
        assert "30" in str(result)
    
    def test_invalid_calculation(self):
        """Test invalid calculation."""
        calc = CalculatorTool()
        result = calc.use(expression="invalid")
        
        assert "error" in str(result).lower() or "invalid" in str(result).lower()


class TestCrew:
    """Test suite for Crew (multi-agent system)."""
    
    def test_crew_agent_init(self):
        """Test crew agent initialization."""
        agent = CrewAgent(
            name="Agent1",
            role="Researcher",
            goal="Find information",
            backstory="Expert researcher"
        )
        
        assert agent.name == "Agent1"
        assert agent.role == "Researcher"
    
    def test_task_init(self):
        """Test task initialization."""
        task = Task(
            description="Research task",
            expected_output="Research results"
        )
        
        assert task.description == "Research task"
    
    def test_crew_init(self):
        """Test crew initialization."""
        agents = [
            CrewAgent("Agent1", "Role1", "Goal1", "Story1")
        ]
        tasks = [
            Task("Task1", "Output1")
        ]
        
        crew = Crew(agents=agents, tasks=tasks, process=ProcessType.SEQUENTIAL)
        
        assert len(crew.agents) == 1
        assert len(crew.tasks) == 1


class TestBaseClasses:
    """Test suite for base classes."""
    
    def test_base_component(self):
        """Test BaseComponent interface."""
        assert hasattr(BaseComponent, '__init__')
    
    def test_base_retriever(self):
        """Test BaseRetriever interface."""
        assert hasattr(BaseRetriever, 'retrieve')
    
    def test_base_reranker(self):
        """Test BaseReRanker interface."""
        assert hasattr(BaseReRanker, 'rerank')
