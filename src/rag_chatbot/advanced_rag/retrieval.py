"""Advanced retrieval strategies combining multiple approaches.

This module implements hybrid search combining semantic (vector)
and lexical (BM25) retrieval using Reciprocal Rank Fusion.
"""

import logging
from typing import List, Dict
from collections import defaultdict
from ..base import BaseRetriever
from ..interfaces import Documento, IVectorStore, IEmbeddingModel

logger = logging.getLogger(__name__)


class BM25Retriever:
    """Simple BM25 (Best Match 25) lexical retriever.
    
    This is a basic implementation for demonstration.
    In production, consider using libraries like rank-bm25.
    """
    
    def __init__(self, documents: List[Documento] = None):
        """Initialize BM25 retriever.
        
        Args:
            documents: Optional initial document collection.
        """
        self.documents = documents or []
        self.doc_index = {}
        self._build_index()
    
    def _build_index(self):
        """Build simple term frequency index."""
        for i, doc in enumerate(self.documents):
            words = doc.content.lower().split()
            self.doc_index[doc.metadata.get('id', i)] = {
                'doc': doc,
                'terms': set(words)
            }
    
    def add_documents(self, documents: List[Documento]):
        """Add documents to the index.
        
        Args:
            documents: Documents to add.
        """
        self.documents.extend(documents)
        self._build_index()
    
    def retrieve(self, query_text: str, top_k: int = 10) -> List[Documento]:
        """Retrieve documents using simple term matching.
        
        Args:
            query_text: Search query.
            top_k: Number of documents to retrieve.
            
        Returns:
            List of matched documents.
        """
        query_terms = set(query_text.lower().split())
        
        # Score documents by term overlap
        scores = []
        for doc_id, doc_data in self.doc_index.items():
            overlap = len(query_terms & doc_data['terms'])
            if overlap > 0:
                scores.append((overlap, doc_data['doc']))
        
        # Sort by score descending
        scores.sort(key=lambda x: x[0], reverse=True)
        
        return [doc for score, doc in scores[:top_k]]


class VectorRetriever(BaseRetriever):
    """Vector-based semantic retriever.
    
    Uses embedding similarity for retrieval.
    """
    
    def __init__(self, vector_store: IVectorStore, embedder: IEmbeddingModel, **config):
        """Initialize vector retriever.
        
        Args:
            vector_store: Vector database.
            embedder: Embedding model.
            **config: Additional configuration.
        """
        super().__init__(vector_store=vector_store, embedder=embedder, **config)
        self.vector_store = vector_store
        self.embedder = embedder
    
    def retrieve(self, query_text: str, top_k: int = 10) -> List[Documento]:
        """Retrieve documents by semantic similarity.
        
        Args:
            query_text: Search query.
            top_k: Number of documents to retrieve.
            
        Returns:
            List of similar documents.
        """
        query_embedding = self.embedder.embed_query(query_text)
        return self.vector_store.search(query_embedding, k=top_k)


class HybridRetriever(BaseRetriever):
    """Hybrid retriever combining vector and lexical search.
    
    Combines semantic (vector) and lexical (BM25) search using
    Reciprocal Rank Fusion (RRF), an effective method that doesn't
    require weight tuning.
    
    References:
        - RRF: "Reciprocal Rank Fusion outperforms individual methods"
        - Hybrid search: "Best of both semantic and keyword matching"
    """
    
    def __init__(
        self,
        vector_retriever: VectorRetriever,
        bm25_retriever: BM25Retriever,
        k_rrf: int = 60,
        **config
    ):
        """Initialize hybrid retriever.
        
        Args:
            vector_retriever: Semantic retriever.
            bm25_retriever: Lexical retriever.
            k_rrf: RRF constant (typically 60).
            **config: Additional configuration.
        """
        super().__init__(
            vector_retriever=vector_retriever,
            bm25_retriever=bm25_retriever,
            k_rrf=k_rrf,
            **config
        )
        self.vector_retriever = vector_retriever
        self.bm25_retriever = bm25_retriever
        self.k_rrf = k_rrf
        logger.info(f"HybridRetriever initialized with k_rrf={k_rrf}")
    
    def retrieve(self, query_text: str, top_k: int = 50) -> List[Documento]:
        """Retrieve documents using hybrid search with RRF.
        
        Args:
            query_text: Search query.
            top_k: Number of documents to retrieve.
            
        Returns:
            Fused and ranked list of documents.
        """
        logger.debug("Executing hybrid retrieval...")
        
        # Get results from both retrievers
        vector_results = self.vector_retriever.retrieve(query_text, top_k=top_k)
        bm25_results = self.bm25_retriever.retrieve(query_text, top_k=top_k)
        
        logger.debug(f"Vector retriever: {len(vector_results)} docs, "
                    f"BM25 retriever: {len(bm25_results)} docs")
        
        # Calculate RRF scores
        rrf_scores = defaultdict(float)
        all_docs = {}
        
        # Process vector search results
        for rank, doc in enumerate(vector_results):
            doc_id = id(doc)  # Use object id as unique identifier
            all_docs[doc_id] = doc
            rrf_scores[doc_id] += 1.0 / (self.k_rrf + rank + 1)
        
        # Process BM25 results
        for rank, doc in enumerate(bm25_results):
            doc_id = id(doc)
            all_docs[doc_id] = doc
            rrf_scores[doc_id] += 1.0 / (self.k_rrf + rank + 1)
        
        # Sort by combined RRF score
        sorted_doc_ids = sorted(
            rrf_scores.keys(),
            key=lambda doc_id: rrf_scores[doc_id],
            reverse=True
        )
        
        final_docs = [all_docs[doc_id] for doc_id in sorted_doc_ids]
        
        logger.debug(f"RRF fusion produced {len(final_docs)} unique documents")
        return final_docs[:top_k]
