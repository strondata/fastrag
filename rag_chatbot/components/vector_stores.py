"""Implementações de Vector Stores."""

import logging
from typing import List
import chromadb

from rag_chatbot.interfaces import IVectorStore, Documento
from rag_chatbot.config import DEFAULT_COLLECTION_NAME

logger = logging.getLogger(__name__)


class ChromaVectorStore(IVectorStore):
    """Vector Store usando ChromaDB.
    
    Armazena e busca vetores de embedding usando ChromaDB.
    """
    
    def __init__(self, collection_name: str = DEFAULT_COLLECTION_NAME, persist_directory: str = None):
        """Inicializa o ChromaDB vector store.
        
        Args:
            collection_name: Nome da coleção no ChromaDB.
            persist_directory: Diretório para persistir dados (None = in-memory).
        """
        logger.info(f"Inicializando ChromaDB com coleção '{collection_name}'")
        
        if persist_directory:
            self.client = chromadb.PersistentClient(path=persist_directory)
        else:
            self.client = chromadb.Client()
        
        # Deletar coleção existente se houver para evitar conflitos
        try:
            self.client.delete_collection(name=collection_name)
        except:
            pass
            
        self.collection = self.client.create_collection(name=collection_name)
        self._doc_counter = 0
        logger.info(f"Coleção ChromaDB '{collection_name}' pronta.")
    
    def add(self, documents: List[Documento], embeddings: List[List[float]]) -> None:
        """Adiciona documentos e seus embeddings ao store.
        
        Args:
            documents: Lista de documentos.
            embeddings: Lista de embeddings correspondentes.
        """
        if not documents:
            logger.warning("Nenhum documento para adicionar.")
            return
        
        # Gerar IDs únicos para os documentos
        ids = [f"doc_{self._doc_counter + i}" for i in range(len(documents))]
        self._doc_counter += len(documents)
        
        # Extrair metadados e conteúdos
        metadatas = [doc.metadata for doc in documents]
        contents = [doc.content for doc in documents]
        
        # Adicionar à coleção
        self.collection.add(
            embeddings=embeddings,
            documents=contents,
            metadatas=metadatas,
            ids=ids
        )
        
        logger.info(f"{len(documents)} documentos adicionados ao RAG.")
    
    def search(self, query_embedding: List[float], k: int) -> List[Documento]:
        """Busca os k documentos mais similares ao query embedding.
        
        Args:
            query_embedding: Vetor de embedding da query.
            k: Número de resultados a retornar.
            
        Returns:
            Lista dos k documentos mais similares.
        """
        logger.debug(f"Buscando top {k} documentos similares.")
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k
        )
        
        # Converter resultados de volta para objetos Documento
        documentos_encontrados = []
        
        if results['documents'] and results['documents'][0]:
            for i, doc_content in enumerate(results['documents'][0]):
                metadata = results['metadatas'][0][i] if results['metadatas'] else {}
                documentos_encontrados.append(
                    Documento(content=doc_content, metadata=metadata)
                )
        
        logger.debug(f"Encontrados {len(documentos_encontrados)} documentos.")
        return documentos_encontrados
