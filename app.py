"""Aplicativo Streamlit para o RAG Chatbot.

Interface web interativa para o sistema de chatbot RAG local.
"""

import streamlit as st
import logging
from pathlib import Path

from rag_chatbot.core import RAGChatbot
from rag_chatbot.components.loaders import FolderLoader
from rag_chatbot.components.embedders import MiniLMEmbedder
from rag_chatbot.components.vector_stores import ChromaVectorStore
from rag_chatbot.components.llms import OllamaLLM
from rag_chatbot.config import DEFAULT_LLM_MODEL

# Configurar página
st.set_page_config(
    page_title="Chatbot RAG Local",
    page_icon="🤖",
    layout="wide"
)

logger = logging.getLogger(__name__)


@st.cache_resource
def inicializar_chatbot(model_name: str = DEFAULT_LLM_MODEL):
    """Inicializa o chatbot (cached para não recarregar).
    
    Args:
        model_name: Nome do modelo LLM a usar.
        
    Returns:
        Instância configurada do RAGChatbot.
    """
    logger.info("Inicializando componentes do chatbot...")
    
    try:
        loader = FolderLoader()
        embedder = MiniLMEmbedder()
        store = ChromaVectorStore(collection_name="streamlit_rag")
        llm = OllamaLLM(model_name=model_name)
        
        chatbot = RAGChatbot(
            loader=loader,
            embedder=embedder,
            store=store,
            llm=llm
        )
        
        logger.info("Chatbot inicializado com sucesso!")
        return chatbot
    
    except Exception as e:
        logger.error(f"Erro ao inicializar chatbot: {e}")
        st.error(f"Erro ao inicializar: {e}")
        return None


def main():
    """Função principal da aplicação Streamlit."""
    
    # Título principal
    st.title("🤖 Chatbot RAG Local Personalizado")
    st.markdown("*Retrieval-Augmented Generation com sua base de conhecimento privada*")
    
    # Sidebar para configuração
    st.sidebar.title("⚙️ Configuração")
    
    # Seleção do modelo LLM
    model_name = st.sidebar.text_input(
        "Modelo LLM (Ollama)",
        value=DEFAULT_LLM_MODEL,
        help="Nome do modelo Ollama instalado (ex: llama3, mistral)"
    )
    
    # Inicializar chatbot
    chatbot = inicializar_chatbot(model_name)
    
    if chatbot is None:
        st.error("⚠️ Não foi possível inicializar o chatbot. Verifique os logs.")
        st.stop()
    
    # Seção de ingestão de dados
    st.sidebar.title("📚 Base de Conhecimento")
    
    data_path = st.sidebar.text_input(
        "Caminho da Pasta de Dados",
        value="./data",
        help="Pasta contendo arquivos .txt ou .md"
    )
    
    if st.sidebar.button("🔄 Alimentar RAG", type="primary"):
        if not Path(data_path).exists():
            st.sidebar.error(f"❌ Pasta não encontrada: {data_path}")
        else:
            with st.sidebar.spinner("📖 Lendo, processando e vetorizando documentos..."):
                try:
                    num_docs = chatbot.ingest_data(data_path)
                    
                    if num_docs > 0:
                        st.sidebar.success(f"✅ RAG alimentado com sucesso!")
                        st.sidebar.info(f"📄 {num_docs} documento(s) processado(s)")
                        st.sidebar.info(f"📁 Fonte: {data_path}")
                    else:
                        st.sidebar.warning("⚠️ Nenhum documento .txt ou .md encontrado na pasta.")
                        
                except Exception as e:
                    st.sidebar.error(f"❌ Falha na ingestão: {e}")
                    logger.error(f"Erro durante ingestão: {e}", exc_info=True)
    
    # Informações adicionais na sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 💡 Como usar:")
    st.sidebar.markdown("""
    1. Adicione arquivos `.txt` ou `.md` na pasta de dados
    2. Clique em **Alimentar RAG**
    3. Faça perguntas no chat!
    """)
    
    st.sidebar.markdown("### 📋 Requisitos:")
    st.sidebar.markdown("""
    - Ollama instalado e rodando
    - Modelo baixado: `ollama pull llama3`
    """)
    
    # Área principal - Interface de Chat
    st.markdown("---")
    
    # Inicializar histórico de mensagens
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Mostrar histórico de mensagens
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Input do usuário
    if prompt := st.chat_input("💬 Faça sua pergunta..."):
        # Adicionar mensagem do usuário ao histórico
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Exibir mensagem do usuário
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Gerar e exibir resposta do assistente
        with st.chat_message("assistant"):
            with st.spinner("🤔 Pensando... (Buscando no RAG e gerando resposta)"):
                try:
                    response = chatbot.ask(prompt)
                    st.markdown(response)
                    
                    # Adicionar resposta ao histórico
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response
                    })
                    
                except Exception as e:
                    error_msg = f"❌ Erro ao gerar resposta: {e}"
                    st.error(error_msg)
                    logger.error(f"Erro ao processar pergunta: {e}", exc_info=True)
    
    # Botão para limpar histórico
    if st.session_state.messages:
        if st.sidebar.button("🗑️ Limpar Histórico"):
            st.session_state.messages = []
            st.rerun()


if __name__ == "__main__":
    main()
