"""Implementações de Embedding Models."""

import logging
from typing import List

from sentence_transformers import SentenceTransformer

from rag_chatbot.interfaces import IEmbeddingModel
from rag_chatbot.config import DEFAULT_EMBEDDING_MODEL

logger = logging.getLogger(__name__)


class MiniLMEmbedder(IEmbeddingModel):
    """Modelo de embedding usando SentenceTransformers.
    
    Usa o modelo all-MiniLM-L6-v2 por padrão, que é leve e eficiente.
    """
    
    def __init__(self, model_name: str = DEFAULT_EMBEDDING_MODEL):
        """Inicializa o modelo de embedding.
        
        Args:
            model_name: Nome do modelo SentenceTransformer a usar.
        """
        logger.info(f"Carregando modelo de embedding: {model_name}")
        self.model = SentenceTransformer(model_name)
        logger.info("Modelo de embedding carregado com sucesso.")
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Gera embeddings para uma lista de textos.
        
        Args:
            texts: Lista de textos para embedar.
            
        Returns:
            Lista de vetores de embedding.
        """
        logger.debug(f"Gerando embeddings para {len(texts)} documentos.")
        embeddings = self.model.encode(texts)
        return embeddings.tolist()
    
    def embed_query(self, text: str) -> List[float]:
        """Gera embedding para uma única query.
        
        Args:
            text: Texto da query.
            
        Returns:
            Vetor de embedding.
        """
        logger.debug(f"Gerando embedding para query: {text[:50]}...")
        embedding = self.model.encode([text])[0]
        return embedding.tolist()
