"""Orquestrador principal do RAG Chatbot."""

import logging
from typing import List

from rag_chatbot.interfaces import (
    IDocumentLoader,
    IEmbeddingModel,
    IVectorStore,
    ILocalLLM,
    Documento
)
from rag_chatbot.config import DEFAULT_TOP_K

logger = logging.getLogger(__name__)


class RAGChatbot:
    """Orquestrador principal do sistema RAG.
    
    Coordena o fluxo de carregamento de dados, embedding, armazenamento
    e geração de respostas usando Retrieval-Augmented Generation.
    
    Segue o princípio SOLID de Inversão de Dependência, aceitando
    interfaces ao invés de implementações concretas.
    """
    
    PROMPT_TEMPLATE = """Use o CONTEXTO abaixo para responder à PERGUNTA.
Se o contexto não ajudar, diga que não sabe.

CONTEXTO:
{context}

PERGUNTA: {question}

RESPOSTA:"""
    
    def __init__(
        self,
        loader: IDocumentLoader,
        embedder: IEmbeddingModel,
        store: IVectorStore,
        llm: ILocalLLM,
        prompt_template: str = None
    ):
        """Inicializa o RAG Chatbot com injeção de dependências.
        
        Args:
            loader: Implementação de IDocumentLoader.
            embedder: Implementação de IEmbeddingModel.
            store: Implementação de IVectorStore.
            llm: Implementação de ILocalLLM.
            prompt_template: Template customizado (opcional).
        """
        self.loader = loader
        self.embedder = embedder
        self.vector_store = store
        self.llm = llm
        self.prompt_template = prompt_template or self.PROMPT_TEMPLATE
        
        logger.info("RAGChatbot instanciado com sucesso.")
    
    def ingest_data(self, path: str) -> int:
        """Processo de alimentar o RAG com dados.
        
        Carrega documentos, gera embeddings e armazena no vector store.
        
        Args:
            path: Caminho da fonte de dados.
            
        Returns:
            Número de documentos ingeridos.
        """
        logger.info(f"Iniciando ingestão de dados de: {path}")
        
        # 1. Carregar documentos
        documents = self.loader.load(path)
        
        if not documents:
            logger.warning("Nenhum documento encontrado para ingestão.")
            return 0
        
        # 2. Gerar embeddings
        logger.info(f"Gerando embeddings para {len(documents)} documentos...")
        contents = [doc.content for doc in documents]
        embeddings = self.embedder.embed_documents(contents)
        
        # 3. Armazenar no vector store
        logger.info("Armazenando documentos no vector store...")
        self.vector_store.add(documents, embeddings)
        
        logger.info(f"Ingestão de dados concluída. {len(documents)} documentos processados.")
        return len(documents)
    
    def ask(self, question: str, k: int = DEFAULT_TOP_K) -> str:
        """Processo de gerar uma resposta para uma pergunta.
        
        Busca contexto relevante e gera resposta usando o LLM.
        
        Args:
            question: A pergunta do usuário.
            k: Número de documentos a recuperar como contexto.
            
        Returns:
            Resposta gerada pelo LLM.
        """
        logger.debug(f"Nova pergunta: {question}")
        
        # 1. Embedar a pergunta
        logger.debug("Gerando embedding da pergunta...")
        query_embedding = self.embedder.embed_query(question)
        
        # 2. Buscar documentos relevantes
        logger.debug(f"Buscando top {k} documentos relevantes...")
        context_documents = self.vector_store.search(query_embedding, k=k)
        
        # 3. Construir contexto
        if not context_documents:
            logger.warning("Nenhum documento encontrado no contexto.")
            context_str = "Nenhuma informação disponível."
        else:
            context_texts = [doc.content for doc in context_documents]
            context_str = "\n---\n".join(context_texts)
            logger.debug(f"Contexto construído com {len(context_documents)} documentos.")
        
        # 4. Construir prompt
        prompt = self.prompt_template.format(
            context=context_str,
            question=question
        )
        
        # 5. Gerar resposta
        logger.debug("Gerando resposta com LLM...")
        response = self.llm.generate(prompt)
        logger.debug(f"Resposta gerada: {response[:100]}...")
        
        return response
    
    def get_sources(self, question: str, k: int = DEFAULT_TOP_K) -> List[Documento]:
        """Retorna os documentos fonte usados para responder uma pergunta.
        
        Útil para rastreabilidade e debugging.
        
        Args:
            question: A pergunta do usuário.
            k: Número de documentos a recuperar.
            
        Returns:
            Lista de documentos fonte.
        """
        query_embedding = self.embedder.embed_query(question)
        return self.vector_store.search(query_embedding, k=k)
