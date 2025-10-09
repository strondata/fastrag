"""
Utility functions for FastRAG.
"""

from typing import List, Any


def chunk_text(text: str, chunk_size: int = 512, overlap: int = 50) -> List[str]:
    """
    Split text into chunks with optional overlap.
    
    Args:
        text: Text to chunk
        chunk_size: Size of each chunk
        overlap: Number of characters to overlap between chunks
        
    Returns:
        List of text chunks
    """
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
        
    return chunks


def preprocess_text(text: str) -> str:
    """
    Preprocess text for RAG pipeline.
    
    Args:
        text: Input text
        
    Returns:
        Preprocessed text
    """
    # Basic preprocessing - remove extra whitespace
    text = " ".join(text.split())
    return text.strip()
