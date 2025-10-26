"""Base component abstractions for the FastRAG framework.

This module defines the base classes for all components in the framework,
enabling modular, composable, and testable RAG pipelines.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List
from rag_chatbot.interfaces import Documento


class BaseComponent(ABC):
    """Base class for all framework components.
    
    Provides a common interface for configuration and execution,
    enabling component swapping and declarative pipeline construction.
    """
    
    def __init__(self, **config):
        """Initialize component with configuration.
        
        Args:
            **config: Component-specific configuration parameters.
        """
        self.config = config
    
    @abstractmethod
    def run(self, data, **kwargs):
        """Execute the component's main functionality.
        
        Args:
            data: Input data to process.
            **kwargs: Additional runtime parameters.
            
        Returns:
            Processed output.
        """
        raise NotImplementedError("Each component must implement the 'run' method.")


class BaseChunker(BaseComponent):
    """Base interface for text segmentation strategies."""
    
    @abstractmethod
    def chunk(self, document_text: str) -> List[str]:
        """Divide text into chunks.
        
        Args:
            document_text: Text to be chunked.
            
        Returns:
            List of text chunks.
        """
        pass
    
    def run(self, data, **kwargs):
        """Execute chunking operation.
        
        Args:
            data: Document text or list of texts.
            **kwargs: Additional parameters.
            
        Returns:
            List of chunks.
        """
        if isinstance(data, str):
            return self.chunk(data, **kwargs)
        elif isinstance(data, list):
            all_chunks = []
            for text in data:
                all_chunks.extend(self.chunk(text, **kwargs))
            return all_chunks
        else:
            raise ValueError("Data must be string or list of strings")


class BaseRetriever(BaseComponent):
    """Base interface for information retrieval algorithms."""
    
    @abstractmethod
    def retrieve(self, query_text: str, top_k: int = 10) -> List[Documento]:
        """Retrieve relevant documents for a query.
        
        Args:
            query_text: Search query.
            top_k: Number of documents to retrieve.
            
        Returns:
            List of relevant documents.
        """
        pass
    
    def run(self, data, **kwargs):
        """Execute retrieval operation.
        
        Args:
            data: Query text.
            **kwargs: Additional parameters (e.g., top_k).
            
        Returns:
            List of retrieved documents.
        """
        return self.retrieve(data, **kwargs)


class BaseReRanker(BaseComponent):
    """Base interface for document re-ranking algorithms."""
    
    @abstractmethod
    def rerank(self, query_text: str, documents: List[Documento], top_n: int = 5) -> List[Documento]:
        """Re-rank documents by relevance.
        
        Args:
            query_text: Search query.
            documents: Documents to re-rank.
            top_n: Number of top documents to return.
            
        Returns:
            Re-ranked list of documents.
        """
        pass
    
    def run(self, data, **kwargs):
        """Execute re-ranking operation.
        
        Args:
            data: Dictionary with 'query' and 'documents' keys.
            **kwargs: Additional parameters (e.g., top_n).
            
        Returns:
            Re-ranked list of documents.
        """
        if isinstance(data, dict):
            query = data.get('query', '')
            documents = data.get('documents', [])
            return self.rerank(query, documents, **kwargs)
        else:
            raise ValueError("Data must be a dictionary with 'query' and 'documents'")


class BaseGenerator(BaseComponent):
    """Base interface for language model generators."""
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from a prompt.
        
        Args:
            prompt: Input prompt.
            **kwargs: Generation parameters (temperature, max_tokens, etc.).
            
        Returns:
            Generated text.
        """
        pass
    
    def run(self, data, **kwargs):
        """Execute generation operation.
        
        Args:
            data: Prompt text.
            **kwargs: Generation parameters.
            
        Returns:
            Generated text.
        """
        return self.generate(data, **kwargs)
