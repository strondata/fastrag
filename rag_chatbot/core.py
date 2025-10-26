"""Orquestrador principal do RAG Chatbot."""

import logging
import base64
from typing import List, Dict, Any, Optional

from rag_chatbot.interfaces import (
    IDocumentLoader,
    IEmbeddingModel,
    IVectorStore,
    ILocalLLM,
    ITextSplitter,
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
    
    PROMPT_TEMPLATE_WITH_HISTORY = """Use o CONTEXTO abaixo e o HISTÓRICO da conversa para responder à PERGUNTA.
Se o contexto não ajudar, diga que não sabe.

HISTÓRICO:
{chat_history}

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
        text_splitter: ITextSplitter = None,
        prompt_template: str = None
    ):
        """Inicializa o RAG Chatbot com injeção de dependências.
        
        Args:
            loader: Implementação de IDocumentLoader.
            embedder: Implementação de IEmbeddingModel.
            store: Implementação de IVectorStore.
            llm: Implementação de ILocalLLM.
            text_splitter: Implementação de ITextSplitter (opcional).
            prompt_template: Template customizado (opcional).
        """
        self.loader = loader
        self.embedder = embedder
        self.vector_store = store
        self.llm = llm
        self.text_splitter = text_splitter
        self.prompt_template = prompt_template or self.PROMPT_TEMPLATE
        
        logger.info("RAGChatbot instanciado com sucesso.")
        if text_splitter:
            logger.info("Text splitter configurado para divisão de documentos.")
    
    def ingest_data(self, path: str) -> int:
        """Processo de alimentar o RAG com dados.
        
        Carrega documentos, gera embeddings e armazena no vector store.
        
        Args:
            path: Caminho da fonte de dados.
            
        Returns:
            Número de documentos/chunks ingeridos.
        """
        logger.info(f"Iniciando ingestão de dados de: {path}")
        
        # 1. Carregar documentos
        documents = self.loader.load(path)
        
        if not documents:
            logger.warning("Nenhum documento encontrado para ingestão.")
            return 0
        
        # 2. Dividir documentos (se text_splitter configurado)
        if self.text_splitter:
            logger.info(f"Dividindo {len(documents)} documentos em chunks...")
            documents = self.text_splitter.split_documents(documents)
            logger.info(f"Após divisão: {len(documents)} chunks.")
        
        # 3. Gerar embeddings
        logger.info(f"Gerando embeddings para {len(documents)} documentos...")
        contents = [doc.content for doc in documents]
        embeddings = self.embedder.embed_documents(contents)
        
        # 4. Armazenar no vector store
        logger.info("Armazenando documentos no vector store...")
        self.vector_store.add(documents, embeddings)
        
        logger.info(f"Ingestão de dados concluída. {len(documents)} documentos processados.")
        return len(documents)
    
    def ask(
        self, 
        question: str, 
        k: int = DEFAULT_TOP_K,
        image_data: bytes = None,
        chat_history: List[Dict[str, str]] = None
    ) -> str:
        """Processo de gerar uma resposta para uma pergunta.
        
        Busca contexto relevante e gera resposta usando o LLM.
        
        Args:
            question: A pergunta do usuário.
            k: Número de documentos a recuperar como contexto.
            image_data: Dados da imagem em bytes (opcional, para modelos multimodais).
            chat_history: Histórico de conversa (opcional).
            
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
        
        # 4. Construir prompt (com ou sem histórico)
        if chat_history:
            prompt = self._create_prompt_with_history(
                context_str, 
                question, 
                chat_history
            )
        else:
            prompt = self.prompt_template.format(
                context=context_str,
                question=question
            )
        
        # 5. Processar imagem se fornecida
        images_base64 = None
        if image_data:
            logger.debug("Convertendo imagem para base64...")
            images_base64 = [base64.b64encode(image_data).decode('utf-8')]
        
        # 6. Gerar resposta
        logger.debug("Gerando resposta com LLM...")
        response = self.llm.generate(prompt, images_base64=images_base64)
        logger.debug(f"Resposta gerada: {response[:100]}...")
        
        return response
    
    def _create_prompt_with_history(
        self, 
        context: str, 
        question: str, 
        chat_history: List[Dict[str, str]]
    ) -> str:
        """Cria um prompt incluindo histórico de conversa.
        
        Args:
            context: Contexto recuperado do RAG.
            question: Pergunta atual.
            chat_history: Lista de mensagens anteriores.
            
        Returns:
            Prompt formatado com histórico.
        """
        # Formatar histórico de chat
        history_lines = []
        for msg in chat_history:
            role = msg.get("role", "")
            content = msg.get("content", "")
            
            if role == "user":
                history_lines.append(f"Usuário: {content}")
            elif role == "assistant":
                history_lines.append(f"Assistente: {content}")
        
        chat_history_str = "\n".join(history_lines) if history_lines else "Nenhum histórico."
        
        # Usar template com histórico
        return self.PROMPT_TEMPLATE_WITH_HISTORY.format(
            chat_history=chat_history_str,
            context=context,
            question=question
        )
    
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
