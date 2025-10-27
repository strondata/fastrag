"""Query transformation techniques for improved retrieval.

This module implements advanced query transformation methods including
Multi-Query generation, Step-back prompting, and HyDE (Hypothetical
Document Embeddings) to enhance retrieval accuracy.
"""

import logging
from typing import List
from ..base import BaseComponent
from ..interfaces import ILocalLLM

logger = logging.getLogger(__name__)


class QueryTransformer(BaseComponent):
    """Transform user queries to improve retrieval quality.
    
    Implements multiple query transformation techniques:
    - Multi-Query: Generate query variations
    - Step-back: Create broader conceptual queries
    - HyDE: Generate hypothetical answer documents
    
    References:
        - Multi-Query: "Query expansion improves recall"
        - Step-back: "Abstract reasoning enhances retrieval"
        - HyDE: "Hypothetical documents bridge query-document gap"
    """
    
    def __init__(self, llm: ILocalLLM, **config):
        """Initialize query transformer.
        
        Args:
            llm: Language model for query generation.
            **config: Additional configuration.
        """
        super().__init__(llm=llm, **config)
        self.llm = llm
        logger.info("QueryTransformer initialized")
    
    def generate_multi_queries(self, query_text: str, num_variations: int = 3) -> List[str]:
        """Generate multiple variations of a query.
        
        Args:
            query_text: Original query.
            num_variations: Number of variations to generate.
            
        Returns:
            List of query variations including the original.
        """
        prompt = f"""Generate {num_variations} different ways to ask the following question.
Each variation should use different wording but ask for the same information.
Return only the variations, one per line.

Original question: {query_text}

Variations:"""
        
        try:
            response = self.llm.generate(prompt)
            variations = [line.strip() for line in response.split('\n') if line.strip()]
            
            # Ensure we return the original query plus variations
            all_queries = [query_text] + variations[:num_variations]
            
            logger.debug(f"Generated {len(all_queries)} query variations")
            return all_queries
        except Exception as e:
            logger.warning(f"Failed to generate query variations: {e}")
            return [query_text]
    
    def generate_step_back_question(self, query_text: str) -> List[str]:
        """Generate a broader, more general version of the query.
        
        Step-back prompting helps retrieve documents about underlying
        principles and concepts.
        
        Args:
            query_text: Original specific query.
            
        Returns:
            List containing original and step-back query.
        """
        prompt = f"""Given the following specific question, generate a broader, more general question 
about the underlying principles or concepts. The general question should help understand 
the fundamentals needed to answer the specific question.

Specific question: {query_text}

General question:"""
        
        try:
            step_back_query = self.llm.generate(prompt).strip()
            
            logger.debug(f"Generated step-back question: {step_back_query[:50]}...")
            return [query_text, step_back_query]
        except Exception as e:
            logger.warning(f"Failed to generate step-back question: {e}")
            return [query_text]
    
    def generate_hypothetical_document(self, query_text: str) -> str:
        """Generate a hypothetical answer document.
        
        HyDE (Hypothetical Document Embeddings) generates a fake answer
        that can be embedded and used for semantic search. This bridges
        the gap between query style and document style.
        
        Args:
            query_text: User's question.
            
        Returns:
            Hypothetical answer document.
        """
        prompt = f"""Write a detailed, informative answer to the following question.
The answer should be factual and comprehensive, as if from a knowledge base document.

Question: {query_text}

Answer:"""
        
        try:
            hyde_document = self.llm.generate(prompt).strip()
            
            logger.debug(f"Generated HyDE document ({len(hyde_document)} chars)")
            return hyde_document
        except Exception as e:
            logger.warning(f"Failed to generate HyDE document: {e}")
            return query_text
    
    def run(self, data, method: str = "multi_query", **kwargs):
        """Execute query transformation.
        
        Args:
            data: Query text.
            method: Transformation method ('multi_query', 'step_back', 'hyde').
            **kwargs: Method-specific parameters.
            
        Returns:
            Transformed query or queries.
        """
        if method == "multi_query":
            return self.generate_multi_queries(data, **kwargs)
        elif method == "step_back":
            return self.generate_step_back_question(data)
        elif method == "hyde":
            return self.generate_hypothetical_document(data)
        else:
            raise ValueError(f"Unknown transformation method: {method}")
