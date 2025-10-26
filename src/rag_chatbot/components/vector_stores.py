"""Implementações de Vector Stores."""

import logging
import hashlib
from typing import List
import chromadb

from ..interfaces import IVectorStore, Documento
from ..config import DEFAULT_COLLECTION_NAME, CHROMA_PERSIST_DIRECTORY

logger = logging.getLogger(__name__)


class ChromaVectorStore(IVectorStore):
    """Vector Store usando ChromaDB.
    
    Armazena e busca vetores de embedding usando ChromaDB.
    """
    
    def __init__(self, collection_name: str = DEFAULT_COLLECTION_NAME, persist_directory: str = None):
        """Inicializa o ChromaDB vector store.
        
        Args:
            collection_name: Nome da coleção no ChromaDB.
            persist_directory: Diretório para persistir dados (None = usa default do config).
        """
        logger.info(f"Inicializando ChromaDB com coleção '{collection_name}'")
        
        # Use o diretório de persistência do config se não for especificado
        if persist_directory is None:
            persist_directory = str(CHROMA_PERSIST_DIRECTORY)
        
        if persist_directory:
            self.client = chromadb.PersistentClient(path=persist_directory)
            logger.info(f"ChromaDB em modo persistente: {persist_directory}")
        else:
            self.client = chromadb.Client()
            logger.info("ChromaDB em modo in-memory")
        
        # Usar get_or_create_collection em vez de deletar e criar
        self.collection = self.client.get_or_create_collection(name=collection_name)
        logger.info(f"Coleção ChromaDB '{collection_name}' pronta.")
    
    def _generate_doc_id(self, document: Documento) -> str:
        """Gera um ID único baseado no hash do conteúdo e metadados do documento.
        
        Args:
            document: Documento para gerar ID.
            
        Returns:
            ID único como string.
        """
        # Criar hash baseado no caminho do arquivo se disponível, caso contrário do conteúdo
        if 'path' in document.metadata:
            content_to_hash = document.metadata['path']
        else:
            content_to_hash = document.content[:500]  # Primeiros 500 chars para hash
        
        hash_obj = hashlib.md5(content_to_hash.encode('utf-8'))
        return f"doc_{hash_obj.hexdigest()}"
    
    def add(self, documents: List[Documento], embeddings: List[List[float]]) -> None:
        """Adiciona documentos e seus embeddings ao store usando upsert.
        
        Args:
            documents: Lista de documentos.
            embeddings: Lista de embeddings correspondentes.
        """
        if not documents:
            logger.warning("Nenhum documento para adicionar.")
            return
        
        # Gerar IDs únicos baseados em hash dos documentos
        ids = [self._generate_doc_id(doc) for doc in documents]
        
        # Extrair metadados e conteúdos
        metadatas = [doc.metadata for doc in documents]
        contents = [doc.content for doc in documents]
        
        # Usar upsert em vez de add para evitar duplicatas
        self.collection.upsert(
            embeddings=embeddings,
            documents=contents,
            metadatas=metadatas,
            ids=ids
        )
        
        logger.info(f"{len(documents)} documentos adicionados/atualizados no RAG.")
    
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
