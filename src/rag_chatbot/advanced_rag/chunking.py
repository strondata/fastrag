"""Advanced chunking strategies for document segmentation.

This module provides semantic-aware chunking that groups text
based on meaning rather than arbitrary size limits.
"""

import re
import logging
from typing import List
import numpy as np
from ..base import BaseChunker
from ..interfaces import IEmbeddingModel

logger = logging.getLogger(__name__)


def split_into_sentences(text: str) -> List[str]:
    """Split text into sentences using basic regex patterns.
    
    Args:
        text: Input text.
        
    Returns:
        List of sentences.
    """
    # Simple sentence splitter - handles common cases
    # Split on period, exclamation, or question mark followed by space/newline
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    # Filter out empty sentences
    return [s.strip() for s in sentences if s.strip()]


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Calculate cosine similarity between two vectors.
    
    Args:
        vec1: First vector.
        vec2: Second vector.
        
    Returns:
        Cosine similarity score (0 to 1).
    """
    vec1_np = np.array(vec1)
    vec2_np = np.array(vec2)
    
    dot_product = np.dot(vec1_np, vec2_np)
    norm1 = np.linalg.norm(vec1_np)
    norm2 = np.linalg.norm(vec2_np)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    return dot_product / (norm1 * norm2)


class SemanticChunker(BaseChunker):
    """Semantic-aware text chunker.
    
    Groups sentences based on semantic similarity rather than
    fixed size, creating thematically coherent chunks that improve
    retrieval quality.
    
    References:
        - Semantic chunking improves context coherence
        - Embedding-based segmentation maintains topic boundaries
    """
    
    def __init__(self, embedding_model: IEmbeddingModel, similarity_threshold: float = 0.75, **config):
        """Initialize semantic chunker.
        
        Args:
            embedding_model: Model for generating sentence embeddings.
            similarity_threshold: Minimum similarity to keep sentences together (0-1).
            **config: Additional configuration.
        """
        super().__init__(
            embedding_model=embedding_model,
            similarity_threshold=similarity_threshold,
            **config
        )
        self.embedding_model = embedding_model
        self.similarity_threshold = similarity_threshold
        logger.info(f"SemanticChunker initialized with threshold={similarity_threshold}")
    
    def chunk(self, document_text: str, similarity_threshold: float = None) -> List[str]:
        """Segment text into semantically coherent chunks.
        
        Args:
            document_text: Text to chunk.
            similarity_threshold: Override default threshold.
            
        Returns:
            List of text chunks.
        """
        threshold = similarity_threshold if similarity_threshold is not None else self.similarity_threshold
        
        # Split into sentences
        sentences = split_into_sentences(document_text)
        
        if not sentences:
            return []
        
        if len(sentences) == 1:
            return sentences
        
        # Generate embeddings for all sentences
        logger.debug(f"Generating embeddings for {len(sentences)} sentences...")
        sentence_embeddings = self.embedding_model.embed_documents(sentences)
        
        # Group sentences by semantic similarity
        chunks = []
        current_chunk = [sentences[0]]
        
        for i in range(1, len(sentences)):
            # Calculate similarity with previous sentence
            similarity = cosine_similarity(
                sentence_embeddings[i-1],
                sentence_embeddings[i]
            )
            
            logger.debug(f"Similarity between sentence {i-1} and {i}: {similarity:.3f}")
            
            if similarity >= threshold:
                # High similarity - keep in current chunk
                current_chunk.append(sentences[i])
            else:
                # Low similarity - start new chunk
                chunks.append(" ".join(current_chunk))
                current_chunk = [sentences[i]]
        
        # Add the last chunk
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        logger.info(f"Semantic chunking: {len(sentences)} sentences -> {len(chunks)} chunks")
        return chunks
