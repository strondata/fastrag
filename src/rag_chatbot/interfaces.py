"""Interfaces (contratos) para os componentes do RAG Chatbot.

Este módulo define as interfaces abstratas seguindo o princípio SOLID de 
Inversão de Dependência, permitindo substituição e testabilidade.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class Documento:
    """Representa um documento com conteúdo e metadados.
    
    Attributes:
        content: O conteúdo textual do documento.
        metadata: Dicionário com informações adicionais (source, etc.).
    """
    content: str
    metadata: Dict[str, Any]


class IDocumentLoader(ABC):
    """Interface para carregamento de documentos de uma fonte."""
    
    @abstractmethod
    def load(self, source: str) -> List[Documento]:
        """Carrega documentos de uma fonte.
        
        Args:
            source: Caminho ou identificador da fonte de dados.
            
        Returns:
            Lista de documentos carregados.
        """
        pass


class IEmbeddingModel(ABC):
    """Interface para modelos de embedding de texto."""
    
    @abstractmethod
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Gera embeddings para uma lista de textos.
        
        Args:
            texts: Lista de textos para embedar.
            
        Returns:
            Lista de vetores de embedding.
        """
        pass
    
    @abstractmethod
    def embed_query(self, text: str) -> List[float]:
        """Gera embedding para uma única query.
        
        Args:
            text: Texto da query.
            
        Returns:
            Vetor de embedding.
        """
        pass


class IVectorStore(ABC):
    """Interface para armazenamento e busca de vetores."""
    
    @abstractmethod
    def add(self, documents: List[Documento], embeddings: List[List[float]]) -> None:
        """Adiciona documentos e seus embeddings ao store.
        
        Args:
            documents: Lista de documentos.
            embeddings: Lista de embeddings correspondentes.
        """
        pass
    
    @abstractmethod
    def search(self, query_embedding: List[float], k: int) -> List[Documento]:
        """Busca os k documentos mais similares ao query embedding.
        
        Args:
            query_embedding: Vetor de embedding da query.
            k: Número de resultados a retornar.
            
        Returns:
            Lista dos k documentos mais similares.
        """
        pass


class ITextSplitter(ABC):
    """Interface para divisão de documentos em chunks."""
    
    @abstractmethod
    def split_documents(self, docs: List[Documento]) -> List[Documento]:
        """Divide documentos em chunks menores.
        
        Args:
            docs: Lista de documentos a dividir.
            
        Returns:
            Lista de documentos divididos (chunks).
        """
        pass


class ILocalLLM(ABC):
    """Interface para modelos de linguagem locais."""
    
    @abstractmethod
    def generate(self, prompt: str, images_base64: List[str] = None) -> str:
        """Gera texto a partir de um prompt.
        
        Args:
            prompt: O prompt para geração.
            images_base64: Lista de imagens em base64 (opcional, para modelos multimodais).
            
        Returns:
            Texto gerado pelo modelo.
        """
        pass
