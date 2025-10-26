"""Re-ranking components for refining retrieval results.

This module implements cross-encoder based re-ranking to improve
the precision of retrieved documents.
"""

import logging
from typing import List
from rag_chatbot.base import BaseReRanker
from rag_chatbot.interfaces import Documento

logger = logging.getLogger(__name__)


class CrossEncoderReRanker(BaseReRanker):
    """Re-rank documents using a cross-encoder model.
    
    Cross-encoders process query-document pairs jointly, capturing
    more nuanced relevance than bi-encoders used in retrieval.
    This provides more accurate ranking at the cost of speed.
    
    References:
        - Cross-encoders outperform bi-encoders for re-ranking
        - Applied only to top-k results for efficiency
        - Common models: ms-marco-MiniLM, ms-marco-TinyBERT
    """
    
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2", **config):
        """Initialize cross-encoder re-ranker.
        
        Args:
            model_name: HuggingFace model identifier.
            **config: Additional configuration.
        """
        super().__init__(model_name=model_name, **config)
        self.model_name = model_name
        self.model = None  # Lazy loading
        logger.info(f"CrossEncoderReRanker initialized with model: {model_name}")
    
    def _load_model(self):
        """Lazy load the cross-encoder model."""
        if self.model is None:
            try:
                from sentence_transformers import CrossEncoder
                self.model = CrossEncoder(self.model_name)
                logger.info(f"Loaded cross-encoder model: {self.model_name}")
            except ImportError:
                logger.error("sentence-transformers not installed. Install with: pip install sentence-transformers")
                raise
            except Exception as e:
                logger.error(f"Failed to load cross-encoder model: {e}")
                raise
    
    def rerank(self, query_text: str, documents: List[Documento], top_n: int = 5) -> List[Documento]:
        """Re-rank documents using cross-encoder scores.
        
        Args:
            query_text: Search query.
            documents: Documents to re-rank.
            top_n: Number of top documents to return.
            
        Returns:
            Re-ranked documents with scores attached.
        """
        if not documents:
            return []
        
        # Ensure model is loaded
        self._load_model()
        
        # Create query-document pairs
        pairs = [(query_text, doc.content) for doc in documents]
        
        logger.debug(f"Re-ranking {len(documents)} documents...")
        
        # Get relevance scores
        try:
            scores = self.model.predict(pairs)
        except Exception as e:
            logger.error(f"Re-ranking failed: {e}")
            return documents[:top_n]
        
        # Attach scores to documents
        for doc, score in zip(documents, scores):
            if not hasattr(doc, 'metadata'):
                doc.metadata = {}
            doc.metadata['rerank_score'] = float(score)
        
        # Sort by score descending
        sorted_docs = sorted(
            documents,
            key=lambda d: d.metadata.get('rerank_score', 0),
            reverse=True
        )
        
        logger.debug(f"Re-ranking complete. Top score: {sorted_docs[0].metadata.get('rerank_score', 0):.4f}")
        
        return sorted_docs[:top_n]


class MockReRanker(BaseReRanker):
    """Mock re-ranker for testing without model dependencies.
    
    Simply returns the first top_n documents without actual re-ranking.
    """
    
    def __init__(self, **config):
        """Initialize mock re-ranker."""
        super().__init__(**config)
        logger.info("MockReRanker initialized (no actual re-ranking)")
    
    def rerank(self, query_text: str, documents: List[Documento], top_n: int = 5) -> List[Documento]:
        """Mock re-ranking - just return top_n documents.
        
        Args:
            query_text: Search query (ignored).
            documents: Documents to "re-rank".
            top_n: Number of documents to return.
            
        Returns:
            First top_n documents.
        """
        # Add mock scores
        for i, doc in enumerate(documents[:top_n]):
            if not hasattr(doc, 'metadata'):
                doc.metadata = {}
            doc.metadata['rerank_score'] = 1.0 - (i * 0.1)
        
        return documents[:top_n]
