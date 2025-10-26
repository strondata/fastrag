"""Tests for Phase 3 components: tools, agents, and memory."""

import pytest
from unittest.mock import Mock, MagicMock
import time
from src.rag_chatbot.agents.tools import BaseTool, RAGTool, CalculatorTool, MockSearchTool
from src.rag_chatbot.agents.agent import Agent
from src.rag_chatbot.agents.memory import MemoryStream, Memory
from src.rag_chatbot.interfaces import Documento


class TestBaseTool:
    """Tests for BaseTool abstraction."""
    
    def test_tool_initialization(self):
        """Test tool initialization."""
        
        class TestTool(BaseTool):
            def use(self, input_data):
                return f"Processed: {input_data}"
        
        tool = TestTool(name="test_tool", description="A test tool")
        
        assert tool.name == "test_tool"
        assert tool.description == "A test tool"
        assert "test_tool" in str(tool)
    
    def test_tool_requires_use_implementation(self):
        """Test that BaseTool enforces use() implementation."""
        
        class IncompleteTool(BaseTool):
            pass
        
        with pytest.raises(TypeError):
            tool = IncompleteTool(name="incomplete", description="Missing use method")


class TestRAGTool:
    """Tests for RAGTool."""
    
    def test_rag_tool_initialization(self):
        """Test RAGTool initialization."""
        mock_pipeline = Mock()
        
        tool = RAGTool(rag_pipeline=mock_pipeline)
        
        assert tool.name == "knowledge_search"
        assert "knowledge base" in tool.description.lower()
    
    def test_rag_tool_execution(self):
        """Test RAGTool execution."""
        mock_pipeline = Mock()
        mock_pipeline.run.return_value = "Answer from knowledge base"
        
        tool = RAGTool(rag_pipeline=mock_pipeline)
        result = tool.use("What is Python?")
        
        assert result == "Answer from knowledge base"
        mock_pipeline.run.assert_called_once_with("What is Python?")
    
    def test_rag_tool_error_handling(self):
        """Test RAGTool handles errors gracefully."""
        mock_pipeline = Mock()
        mock_pipeline.run.side_effect = Exception("Pipeline error")
        
        tool = RAGTool(rag_pipeline=mock_pipeline)
        result = tool.use("test query")
        
        assert "Error" in result


class TestCalculatorTool:
    """Tests for CalculatorTool."""
    
    def test_calculator_basic_operations(self):
        """Test basic calculator operations."""
        calc = CalculatorTool()
        
        assert calc.use("2 + 2") == "4"
        assert calc.use("10 * 5") == "50"
        assert calc.use("100 / 4") == "25.0"
    
    def test_calculator_error_handling(self):
        """Test calculator handles invalid input."""
        calc = CalculatorTool()
        
        result = calc.use("invalid expression")
        assert "Error" in result


class TestMockSearchTool:
    """Tests for MockSearchTool."""
    
    def test_mock_search(self):
        """Test mock search tool."""
        search = MockSearchTool()
        
        result = search.use("Python programming")
        
        assert "Python programming" in result
        assert "Mock" in result or "placeholder" in result.lower()


class TestAgent:
    """Tests for ReAct Agent."""
    
    @pytest.fixture
    def mock_llm(self):
        """Create a mock LLM."""
        return Mock()
    
    @pytest.fixture
    def mock_tools(self):
        """Create mock tools."""
        calc_tool = CalculatorTool()
        
        search_tool = Mock(spec=BaseTool)
        search_tool.name = "search"
        search_tool.description = "Search for information"
        search_tool.use.return_value = "Search result"
        
        return [calc_tool, search_tool]
    
    def test_agent_initialization(self, mock_llm, mock_tools):
        """Test agent initialization."""
        agent = Agent(llm=mock_llm, tools=mock_tools, max_iterations=5)
        
        assert len(agent.tools) == 2
        assert "calculator" in agent.tools
        assert "search" in agent.tools
        assert agent.max_iterations == 5
    
    def test_agent_parse_thought(self, mock_llm, mock_tools):
        """Test parsing thought from response."""
        agent = Agent(llm=mock_llm, tools=mock_tools)
        
        response = "Thought: I need to calculate the sum\nAction: calculator"
        thought = agent._parse_thought(response)
        
        assert "calculate" in thought.lower()
    
    def test_agent_parse_action(self, mock_llm, mock_tools):
        """Test parsing action from response."""
        agent = Agent(llm=mock_llm, tools=mock_tools)
        
        response = """Thought: I need to use calculator
Action: calculator
Action Input: 5 + 5"""
        
        action, action_input = agent._parse_action(response)
        
        assert action == "calculator"
        assert action_input == "5 + 5"
    
    def test_agent_parse_final_answer(self, mock_llm, mock_tools):
        """Test parsing final answer."""
        agent = Agent(llm=mock_llm, tools=mock_tools)
        
        response = "Thought: I have the answer\nFinal Answer: 42"
        action, answer = agent._parse_action(response)
        
        assert action == "Final Answer"
        assert answer == "42"
    
    def test_agent_run_simple_task(self, mock_llm, mock_tools):
        """Test agent executing a simple task."""
        # Mock LLM to return final answer immediately
        mock_llm.generate.return_value = "Thought: I can answer this\nFinal Answer: The answer is 42"
        
        agent = Agent(llm=mock_llm, tools=mock_tools)
        result = agent.run("What is the answer?")
        
        assert "42" in result
        mock_llm.generate.assert_called_once()
    
    def test_agent_run_with_tool_use(self, mock_llm, mock_tools):
        """Test agent using a tool."""
        # First response: use calculator
        # Second response: final answer
        mock_llm.generate.side_effect = [
            "Thought: Need to calculate\nAction: calculator\nAction Input: 2 + 2",
            "Thought: Got the result\nFinal Answer: The result is 4"
        ]
        
        agent = Agent(llm=mock_llm, tools=mock_tools)
        result = agent.run("What is 2 + 2?")
        
        assert "4" in result
        assert mock_llm.generate.call_count == 2
    
    def test_agent_max_iterations(self, mock_llm, mock_tools):
        """Test agent respects max iterations."""
        # Always return an action, never final answer
        mock_llm.generate.return_value = "Thought: Still thinking\nAction: search\nAction Input: test"
        
        agent = Agent(llm=mock_llm, tools=mock_tools, max_iterations=3)
        result = agent.run("Test query")
        
        # Should stop after max iterations
        assert mock_llm.generate.call_count == 3
        assert "couldn't find" in result.lower() or "max" in result.lower()
    
    def test_agent_add_remove_tool(self, mock_llm, mock_tools):
        """Test adding and removing tools."""
        agent = Agent(llm=mock_llm, tools=mock_tools)
        
        initial_count = len(agent.tools)
        
        # Add new tool
        new_tool = Mock(spec=BaseTool)
        new_tool.name = "new_tool"
        agent.add_tool(new_tool)
        
        assert len(agent.tools) == initial_count + 1
        assert "new_tool" in agent.tools
        
        # Remove tool
        agent.remove_tool("new_tool")
        assert len(agent.tools) == initial_count
        assert "new_tool" not in agent.tools


class TestMemory:
    """Tests for Memory dataclass."""
    
    def test_memory_creation(self):
        """Test memory object creation."""
        memory = Memory(
            content="Test memory",
            importance=8.0,
            timestamp=time.time(),
            metadata={"source": "test"}
        )
        
        assert memory.content == "Test memory"
        assert memory.importance == 8.0
        assert "id" in memory.metadata
        assert memory.metadata["source"] == "test"


class TestMemoryStream:
    """Tests for MemoryStream."""
    
    @pytest.fixture
    def mock_components(self):
        """Create mock components for memory stream."""
        mock_embedder = Mock()
        mock_embedder.embed_query.return_value = [0.1, 0.2, 0.3]
        
        mock_store = Mock()
        mock_store.search.return_value = []
        
        mock_llm = Mock()
        mock_llm.generate.return_value = "7"
        
        return {
            'embedder': mock_embedder,
            'store': mock_store,
            'llm': mock_llm
        }
    
    def test_memory_stream_initialization(self, mock_components):
        """Test memory stream initialization."""
        memory = MemoryStream(
            embedder=mock_components['embedder'],
            vector_store=mock_components['store'],
            llm=mock_components['llm']
        )
        
        # Weights should sum to 1
        total = memory.recency_weight + memory.importance_weight + memory.relevance_weight
        assert abs(total - 1.0) < 0.001
    
    def test_add_memory_with_importance(self, mock_components):
        """Test adding memory with evaluated importance."""
        memory_stream = MemoryStream(
            embedder=mock_components['embedder'],
            vector_store=mock_components['store'],
            llm=mock_components['llm']
        )
        
        memory_stream.add_memory("Important fact", importance=9.0)
        
        # Should embed and store
        mock_components['embedder'].embed_query.assert_called_once()
        mock_components['store'].add.assert_called_once()
    
    def test_add_memory_auto_importance(self, mock_components):
        """Test adding memory with auto-evaluated importance."""
        mock_components['llm'].generate.return_value = "8"
        
        memory_stream = MemoryStream(
            embedder=mock_components['embedder'],
            vector_store=mock_components['store'],
            llm=mock_components['llm']
        )
        
        memory_stream.add_memory("Auto-importance memory")
        
        # Should call LLM to evaluate importance
        mock_components['llm'].generate.assert_called_once()
    
    def test_calculate_recency_score(self, mock_components):
        """Test recency score calculation."""
        memory_stream = MemoryStream(
            embedder=mock_components['embedder'],
            vector_store=mock_components['store']
        )
        
        # Recent memory should have high recency
        recent_timestamp = time.time()
        recency = memory_stream._calculate_recency_score(recent_timestamp)
        assert recency > 0.9
        
        # Old memory should have lower recency
        old_timestamp = time.time() - (24 * 3600)  # 24 hours ago
        recency = memory_stream._calculate_recency_score(old_timestamp)
        assert recency < 0.9
    
    def test_retrieve_memories(self, mock_components):
        """Test memory retrieval with combined scoring."""
        # Mock vector store to return some memories
        mock_docs = [
            Documento(
                content=f"Memory {i}",
                metadata={
                    'timestamp': time.time() - (i * 3600),  # Older memories
                    'importance': 10 - i  # Less important over time
                }
            )
            for i in range(5)
        ]
        
        mock_components['store'].search.return_value = mock_docs
        
        memory_stream = MemoryStream(
            embedder=mock_components['embedder'],
            vector_store=mock_components['store']
        )
        
        retrieved = memory_stream.retrieve_memories("test query", top_k=3)
        
        # Should retrieve top 3
        assert len(retrieved) == 3
        # Should have final scores
        assert all('final_score' in m.metadata for m in retrieved)
        # Should be sorted by final score
        scores = [m.metadata['final_score'] for m in retrieved]
        assert scores == sorted(scores, reverse=True)
