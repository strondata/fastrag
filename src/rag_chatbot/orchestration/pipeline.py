"""Pipeline orchestrator for declarative RAG workflows.

This module provides the Pipeline class for building and executing
RAG workflows in a declarative manner.
"""

import logging
from typing import Optional, List
from ..base import BaseRetriever, BaseReRanker, BaseGenerator
from ..interfaces import Documento

logger = logging.getLogger(__name__)


class Pipeline:
    """Main orchestrator for RAG pipelines.
    
    Coordinates the flow of retrieval, re-ranking, and generation,
    enabling clean, readable, and modifiable RAG workflows.
    
    Example:
        >>> pipeline = Pipeline(
        ...     retriever=my_retriever,
        ...     reranker=my_reranker,
        ...     generator=my_generator
        ... )
        >>> response = pipeline.run("What is RAG?")
    """
    
    DEFAULT_PROMPT_TEMPLATE = """Use the CONTEXT below to answer the QUESTION.
If the context doesn't help, say you don't know.

CONTEXT:
{context}

QUESTION: {question}

ANSWER:"""
    
    def __init__(
        self,
        retriever: BaseRetriever,
        generator: BaseGenerator,
        reranker: Optional[BaseReRanker] = None,
        prompt_template: Optional[str] = None
    ):
        """Initialize the pipeline with components.
        
        Args:
            retriever: Component for retrieving relevant documents.
            generator: Component for generating responses.
            reranker: Optional component for re-ranking documents.
            prompt_template: Optional custom prompt template.
        """
        self.retriever = retriever
        self.reranker = reranker
        self.generator = generator
        self.prompt_template = prompt_template or self.DEFAULT_PROMPT_TEMPLATE
        
        logger.info("Pipeline initialized with retriever, generator" + 
                   (" and reranker" if reranker else ""))
    
    def run(self, query: str, top_k: int = 10, top_n: int = 5) -> str:
        """Execute the complete RAG pipeline.
        
        Args:
            query: User's question.
            top_k: Number of documents to retrieve.
            top_n: Number of documents to use after re-ranking.
            
        Returns:
            Generated response.
        """
        logger.debug(f"Pipeline processing query: {query[:50]}...")
        
        # 1. Retrieve relevant documents
        logger.debug(f"Retrieving top {top_k} documents...")
        retrieved_docs = self.retriever.retrieve(query, top_k=top_k)
        
        if not retrieved_docs:
            logger.warning("No documents retrieved")
            return "I don't have enough information to answer this question."
        
        # 2. (Optional) Re-rank documents for improved precision
        if self.reranker:
            logger.debug(f"Re-ranking documents, selecting top {top_n}...")
            ranked_docs = self.reranker.rerank(query, retrieved_docs, top_n=top_n)
        else:
            ranked_docs = retrieved_docs[:top_n]
        
        # 3. Build prompt with retrieved context
        context = "\n---\n".join([doc.content for doc in ranked_docs])
        prompt = self.prompt_template.format(
            context=context,
            question=query
        )
        
        # 4. Generate final response
        logger.debug("Generating response...")
        response = self.generator.generate(prompt)
        
        logger.debug(f"Pipeline completed, response length: {len(response)}")
        return response
    
    def get_sources(self, query: str, top_k: int = 10, top_n: int = 5) -> List[Documento]:
        """Get source documents without generating a response.
        
        Useful for debugging and transparency.
        
        Args:
            query: User's question.
            top_k: Number of documents to retrieve.
            top_n: Number of documents to return after re-ranking.
            
        Returns:
            List of source documents.
        """
        retrieved_docs = self.retriever.retrieve(query, top_k=top_k)
        
        if self.reranker and retrieved_docs:
            return self.reranker.rerank(query, retrieved_docs, top_n=top_n)
        else:
            return retrieved_docs[:top_n]
