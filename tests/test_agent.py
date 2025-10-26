"""Comprehensive unit tests for agent module."""

import pytest
from unittest.mock import Mock, MagicMock, patch
from rag_chatbot.agent import Agent
from rag_chatbot.tools import BaseTool


class MockTool(BaseTool):
    """Mock tool for testing."""
    
    def __init__(self, name="calculator", description="Calculates things"):
        self.name = name
        self.description = description
    
    def run(self, input_text: str) -> str:
        """Mock run method."""
        return f"Result of {self.name}: {input_text}"


class TestAgent:
    """Test suite for Agent."""
    
    @pytest.fixture
    def mock_llm(self):
        """Create mock LLM."""
        llm = Mock()
        llm.generate.return_value = "Thought: Calculate 2+2\nAction: calculator\nAction Input: 2+2\n"
        return llm
    
    @pytest.fixture
    def mock_tools(self):
        """Create mock tools."""
        return [
            MockTool(name="calculator", description="Performs calculations"),
            MockTool(name="search", description="Searches information")
        ]
    
    def test_init(self, mock_llm, mock_tools):
        """Test agent initialization."""
        agent = Agent(llm=mock_llm, tools=mock_tools, max_iterations=5)
        
        assert agent.llm == mock_llm
        assert len(agent.tools) == 2
        assert agent.max_iterations == 5
        assert "calculator" in agent.tools
        assert "search" in agent.tools
    
    def test_init_with_memory(self, mock_llm, mock_tools):
        """Test initialization with memory."""
        mock_memory = Mock()
        agent = Agent(llm=mock_llm, tools=mock_tools, memory=mock_memory)
        
        assert agent.memory == mock_memory
    
    def test_build_tools_description(self, mock_llm, mock_tools):
        """Test building tools description."""
        agent = Agent(llm=mock_llm, tools=mock_tools)
        
        description = agent._build_tools_description()
        
        assert "calculator" in description
        assert "search" in description
        assert "Performs calculations" in description
    
    def test_parse_thought(self, mock_llm, mock_tools):
        """Test parsing thought from response."""
        agent = Agent(llm=mock_llm, tools=mock_tools)
        
        response = "Thought: I need to calculate\nAction: calculator"
        thought = agent._parse_thought(response)
        
        assert "calculate" in thought.lower()
    
    def test_parse_action(self, mock_llm, mock_tools):
        """Test parsing action from response."""
        agent = Agent(llm=mock_llm, tools=mock_tools)
        
        response = "Thought: Calculate\nAction: calculator\nAction Input: 2+2"
        action = agent._parse_action(response)
        
        assert action == "calculator"
    
    def test_parse_action_input(self, mock_llm, mock_tools):
        """Test parsing action input from response."""
        agent = Agent(llm=mock_llm, tools=mock_tools)
        
        response = "Thought: Calculate\nAction: calculator\nAction Input: 2+2"
        action_input = agent._parse_action_input(response)
        
        assert action_input == "2+2"
    
    def test_parse_final_answer(self, mock_llm, mock_tools):
        """Test parsing final answer from response."""
        agent = Agent(llm=mock_llm, tools=mock_tools)
        
        response = "Thought: I have the answer\nFinal Answer: The result is 4"
        final_answer = agent._parse_final_answer(response)
        
        assert "The result is 4" in final_answer
    
    def test_is_final_answer_true(self, mock_llm, mock_tools):
        """Test detecting final answer."""
        agent = Agent(llm=mock_llm, tools=mock_tools)
        
        response = "Final Answer: Done"
        assert agent._is_final_answer(response) == True
    
    def test_is_final_answer_false(self, mock_llm, mock_tools):
        """Test not detecting final answer when absent."""
        agent = Agent(llm=mock_llm, tools=mock_tools)
        
        response = "Thought: Still thinking"
        assert agent._is_final_answer(response) == False
    
    def test_run_tool(self, mock_llm, mock_tools):
        """Test running a tool."""
        agent = Agent(llm=mock_llm, tools=mock_tools)
        
        result = agent._run_tool("calculator", "2+2")
        
        assert "calculator" in result.lower()
        assert "2+2" in result
    
    def test_run_tool_not_found(self, mock_llm, mock_tools):
        """Test running non-existent tool."""
        agent = Agent(llm=mock_llm, tools=mock_tools)
        
        result = agent._run_tool("nonexistent", "input")
        
        assert "Tool not found" in result or "error" in result.lower()
    
    def test_run_simple_query(self, mock_llm, mock_tools):
        """Test running simple agent query."""
        # Setup LLM to return final answer immediately
        mock_llm.generate.return_value = "Thought: I know the answer\nFinal Answer: 42"
        
        agent = Agent(llm=mock_llm, tools=mock_tools)
        result = agent.run("What is the answer?")
        
        assert "42" in result
    
    def test_max_iterations_limit(self, mock_llm, mock_tools):
        """Test that agent respects max iterations."""
        # Setup LLM to never return final answer
        mock_llm.generate.return_value = "Thought: Keep thinking\nAction: calculator\nAction Input: test"
        
        agent = Agent(llm=mock_llm, tools=mock_tools, max_iterations=2)
        result = agent.run("Test query")
        
        # Should stop after max iterations
        assert mock_llm.generate.call_count <= 3  # Initial + 2 iterations
