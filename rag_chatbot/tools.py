"""Agent tools and abstractions.

This module provides the tool abstraction layer for agents,
allowing them to use various capabilities like RAG, web search, etc.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict
from rag_chatbot.pipeline import Pipeline

logger = logging.getLogger(__name__)


class BaseTool(ABC):
    """Base class for all agent tools.
    
    A tool represents a capability that an agent can use, such as
    searching a knowledge base, calling an API, or performing calculations.
    Each tool has a name, description, and execution method.
    """
    
    def __init__(self, name: str, description: str, **config):
        """Initialize a tool.
        
        Args:
            name: Tool identifier.
            description: Description for the LLM to understand when to use this tool.
            **config: Additional configuration.
        """
        self.name = name
        self.description = description
        self.config = config
        logger.info(f"Tool '{name}' initialized")
    
    @abstractmethod
    def use(self, *args, **kwargs) -> Any:
        """Execute the tool's functionality.
        
        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.
            
        Returns:
            Tool execution result.
        """
        raise NotImplementedError("Each tool must implement the 'use' method")
    
    def __str__(self):
        """String representation of the tool."""
        return f"{self.name}: {self.description}"


class RAGTool(BaseTool):
    """Tool that wraps a RAG pipeline for agent use.
    
    Allows an agent to search a knowledge base and retrieve information.
    """
    
    def __init__(self, rag_pipeline: Pipeline, **config):
        """Initialize RAG tool.
        
        Args:
            rag_pipeline: The RAG pipeline to use.
            **config: Additional configuration.
        """
        super().__init__(
            name="knowledge_search",
            description="Search the knowledge base to answer questions. Input should be a question or query.",
            **config
        )
        self.pipeline = rag_pipeline
    
    def use(self, query: str, **kwargs) -> str:
        """Search the knowledge base.
        
        Args:
            query: Question or search query.
            **kwargs: Additional parameters (top_k, top_n).
            
        Returns:
            Answer from the RAG pipeline.
        """
        logger.debug(f"RAGTool executing query: {query[:50]}...")
        
        try:
            result = self.pipeline.run(query, **kwargs)
            logger.debug(f"RAGTool returned {len(result)} chars")
            return result
        except Exception as e:
            logger.error(f"RAGTool execution failed: {e}")
            return f"Error searching knowledge base: {str(e)}"


class CalculatorTool(BaseTool):
    """Simple calculator tool for mathematical operations."""
    
    def __init__(self, **config):
        """Initialize calculator tool."""
        super().__init__(
            name="calculator",
            description="Perform mathematical calculations. Input should be a mathematical expression like '2 + 2' or '10 * 5'.",
            **config
        )
    
    def use(self, expression: str, **kwargs) -> str:
        """Evaluate a mathematical expression.
        
        Args:
            expression: Mathematical expression to evaluate.
            **kwargs: Additional parameters (ignored).
            
        Returns:
            Result of the calculation as a string.
        """
        logger.debug(f"CalculatorTool evaluating: {expression}")
        
        try:
            # Safe evaluation of mathematical expressions
            # In production, use a proper math parser like sympy
            result = eval(expression, {"__builtins__": {}}, {})
            logger.debug(f"CalculatorTool result: {result}")
            return str(result)
        except Exception as e:
            logger.error(f"CalculatorTool failed: {e}")
            return f"Error in calculation: {str(e)}"


class MockSearchTool(BaseTool):
    """Mock web search tool for demonstration."""
    
    def __init__(self, **config):
        """Initialize mock search tool."""
        super().__init__(
            name="web_search",
            description="Search the web for current information. Input should be a search query.",
            **config
        )
    
    def use(self, query: str, **kwargs) -> str:
        """Mock web search.
        
        Args:
            query: Search query.
            **kwargs: Additional parameters.
            
        Returns:
            Mock search result.
        """
        logger.debug(f"MockSearchTool searching: {query}")
        return f"Mock search results for '{query}': [This is a placeholder. Integrate real search API in production.]"
