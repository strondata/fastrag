"""Aplicativo Streamlit para o RAG Chatbot.

Interface web interativa para o sistema de chatbot RAG local.
"""

import streamlit as st
import logging
from pathlib import Path
from io import BytesIO

from src.rag_chatbot.core import RAGChatbot
from src.rag_chatbot.components.loaders import UniversalLoader
from src.rag_chatbot.components.embedders import MiniLMEmbedder
from src.rag_chatbot.components.vector_stores import ChromaVectorStore
from src.rag_chatbot.components.llms import OllamaLLM
from src.rag_chatbot.components.text_splitters import RecursiveCharacterTextSplitter
from src.rag_chatbot.config import (
    DEFAULT_LLM_MODEL, 
    CHROMA_PERSIST_DIRECTORY,
    CHUNK_SIZE,
    CHUNK_OVERLAP
)

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
        loader = UniversalLoader()
        embedder = MiniLMEmbedder()
        # Usar o diretório de persistência do config
        store = ChromaVectorStore(collection_name="streamlit_rag")
        llm = OllamaLLM(model_name=model_name)
        
        # Adicionar text splitter para divisão inteligente de documentos
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP
        )
        
        chatbot = RAGChatbot(
            loader=loader,
            embedder=embedder,
            store=store,
            llm=llm,
            text_splitter=text_splitter
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
    
    # Sidebar para configuração global
    st.sidebar.title("⚙️ Configurações Globais")
    
    # Seleção do modelo LLM
    model_name = st.sidebar.text_input(
        "Modelo LLM (Ollama)",
        value=DEFAULT_LLM_MODEL,
        help="Nome do modelo Ollama instalado (ex: llama3, mistral)"
    )
    
    # Caminho dos dados
    data_path = st.sidebar.text_input(
        "Caminho da Pasta de Dados",
        value="./data",
        help="Pasta contendo arquivos (.txt, .md, .pdf, .docx)"
    )
    
    # Inicializar chatbot
    chatbot = inicializar_chatbot(model_name)
    
    if chatbot is None:
        st.error("⚠️ Não foi possível inicializar o chatbot. Verifique os logs.")
        st.stop()
    
    # Criar abas
    tab_chat, tab_manage, tab_help = st.tabs(["💬 Chat", "📚 Gerenciar RAG", "💡 Ajuda"])
    
    # ========== ABA: CHAT ==========
    with tab_chat:
        st.markdown("### Chat com RAG")
        st.markdown("Faça perguntas baseadas nos documentos da sua base de conhecimento.")
        
        # Upload de imagem (opcional, para modelos multimodais)
        uploaded_image = st.file_uploader(
            "🖼️ Enviar imagem (opcional, para análise com modelo multimodal)",
            type=["png", "jpg", "jpeg"],
            help="O modelo multimodal (ex: llava) analisará a imagem junto com o contexto do RAG"
        )
        
        # Mostrar preview da imagem se carregada
        if uploaded_image:
            st.image(uploaded_image, caption="Imagem enviada", width=300)
        
        # Inicializar histórico de mensagens
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        # Mostrar histórico de mensagens
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                # Mostrar imagem se houver
                if "image" in message and message["image"]:
                    st.image(message["image"], caption="Imagem enviada pelo usuário", width=300)
                
                st.markdown(message["content"])
                
                # Mostrar fontes se disponível
                if message["role"] == "assistant" and "sources" in message:
                    with st.expander("📚 Ver fontes utilizadas"):
                        for i, source in enumerate(message["sources"], 1):
                            st.markdown(f"**Fonte {i}:**")
                            st.markdown(f"- **Arquivo:** {source.metadata.get('source', 'N/A')}")
                            st.markdown(f"- **Caminho:** {source.metadata.get('path', 'N/A')}")
                            
                            # Mostrar informações de chunk se disponível
                            if 'chunk_index' in source.metadata:
                                chunk_idx = source.metadata.get('chunk_index', 0)
                                total_chunks = source.metadata.get('total_chunks', 1)
                                st.markdown(f"- **Chunk:** {chunk_idx + 1} de {total_chunks}")
                            
                            st.markdown(f"- **Trecho:** {source.content[:200]}...")
                            st.markdown("---")
        
        # Input do usuário
        if prompt := st.chat_input("💬 Faça sua pergunta..."):
            # Processar imagem se houver
            image_data = None
            image_for_display = None
            
            if uploaded_image:
                # Ler dados da imagem
                image_data = uploaded_image.read()
                # Guardar para exibição
                uploaded_image.seek(0)
                image_for_display = uploaded_image
            
            # Adicionar mensagem do usuário ao histórico
            user_message = {
                "role": "user", 
                "content": prompt,
                "image": image_for_display
            }
            st.session_state.messages.append(user_message)
            
            # Exibir mensagem do usuário
            with st.chat_message("user"):
                if image_for_display:
                    st.image(image_for_display, caption="Imagem enviada pelo usuário", width=300)
                st.markdown(prompt)
            
            # Gerar e exibir resposta do assistente
            with st.chat_message("assistant"):
                with st.spinner("🤔 Pensando... (Buscando no RAG e gerando resposta)"):
                    try:
                        # Passar histórico de chat (sem imagens para o histórico)
                        chat_history = [
                            {"role": msg["role"], "content": msg["content"]} 
                            for msg in st.session_state.messages[:-1]  # Excluir a pergunta atual
                        ]
                        
                        # Fazer pergunta com contexto conversacional e imagem (se houver)
                        response = chatbot.ask(
                            prompt, 
                            image_data=image_data,
                            chat_history=chat_history if chat_history else None
                        )
                        sources = chatbot.get_sources(prompt)
                        
                        st.markdown(response)
                        
                        # Adicionar resposta ao histórico com fontes
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": response,
                            "sources": sources,
                            "image": None
                        })
                        
                        # Mostrar fontes
                        if sources:
                            with st.expander("📚 Ver fontes utilizadas"):
                                for i, source in enumerate(sources, 1):
                                    st.markdown(f"**Fonte {i}:**")
                                    st.markdown(f"- **Arquivo:** {source.metadata.get('source', 'N/A')}")
                                    st.markdown(f"- **Caminho:** {source.metadata.get('path', 'N/A')}")
                                    st.markdown(f"- **Trecho:** {source.content[:200]}...")
                                    st.markdown("---")
                        
                    except Exception as e:
                        error_msg = f"❌ Erro ao gerar resposta: {e}"
                        st.error(error_msg)
                        logger.error(f"Erro ao processar pergunta: {e}", exc_info=True)
    
    # ========== ABA: GERENCIAR RAG ==========
    with tab_manage:
        st.markdown("### Gerenciar Base de Conhecimento")
        
        # Seção de ingestão
        st.markdown("#### 📥 Alimentar RAG com Documentos")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.info(f"📁 Pasta atual: **{data_path}**")
            
            if Path(data_path).exists():
                # Buscar arquivos de todos os formatos suportados
                files = (
                    list(Path(data_path).glob("*.txt")) + 
                    list(Path(data_path).glob("*.md")) +
                    list(Path(data_path).glob("*.pdf")) +
                    list(Path(data_path).glob("*.docx"))
                )
                if files:
                    st.success(f"✅ {len(files)} arquivo(s) encontrado(s)")
                    with st.expander("Ver arquivos"):
                        for file in files:
                            st.text(f"- {file.name} ({file.suffix})")
                else:
                    st.warning("⚠️ Nenhum arquivo suportado (.txt, .md, .pdf, .docx) encontrado na pasta")
            else:
                st.error(f"❌ Pasta não encontrada: {data_path}")
        
        with col2:
            if st.button("🔄 Alimentar RAG", type="primary", use_container_width=True):
                if not Path(data_path).exists():
                    st.error(f"❌ Pasta não encontrada: {data_path}")
                else:
                    with st.spinner("📖 Lendo, processando e vetorizando documentos..."):
                        try:
                            num_docs = chatbot.ingest_data(data_path)
                            
                            if num_docs > 0:
                                st.success(f"✅ RAG alimentado com sucesso!")
                                st.info(f"📄 {num_docs} chunk(s) processado(s)")
                                st.info(f"📁 Fonte: {data_path}")
                                st.info(f"💾 Persistido em: {CHROMA_PERSIST_DIRECTORY}")
                                st.info(f"✂️ Divisão inteligente: {CHUNK_SIZE} chars, overlap {CHUNK_OVERLAP}")
                            else:
                                st.warning("⚠️ Nenhum documento suportado encontrado na pasta.")
                                
                        except Exception as e:
                            st.error(f"❌ Falha na ingestão: {e}")
                            logger.error(f"Erro durante ingestão: {e}", exc_info=True)
        
        st.markdown("---")
        
        # Seção de inspeção
        st.markdown("#### 🔍 Inspecionar Fontes")
        st.markdown("Veja quais fontes seriam recuperadas para uma pergunta, sem chamar o LLM.")
        
        inspect_query = st.text_input("Digite uma pergunta para inspecionar:", key="inspect_query")
        inspect_k = st.slider("Número de fontes a recuperar:", min_value=1, max_value=10, value=3, key="inspect_k")
        
        if st.button("🔎 Buscar Fontes", type="secondary"):
            if inspect_query:
                with st.spinner("Buscando fontes..."):
                    try:
                        sources = chatbot.get_sources(inspect_query, k=inspect_k)
                        
                        if sources:
                            st.success(f"✅ Encontradas {len(sources)} fonte(s)")
                            
                            for i, source in enumerate(sources, 1):
                                with st.container():
                                    st.markdown(f"### 📄 Fonte {i}")
                                    st.markdown(f"**Arquivo:** {source.metadata.get('source', 'N/A')}")
                                    st.markdown(f"**Caminho:** {source.metadata.get('path', 'N/A')}")
                                    st.markdown("**Conteúdo:**")
                                    st.text_area(
                                        f"Conteúdo da fonte {i}",
                                        value=source.content,
                                        height=150,
                                        key=f"source_{i}",
                                        label_visibility="collapsed"
                                    )
                                    st.markdown("---")
                        else:
                            st.warning("⚠️ Nenhuma fonte encontrada. Certifique-se de que o RAG foi alimentado.")
                            
                    except Exception as e:
                        st.error(f"❌ Erro ao buscar fontes: {e}")
                        logger.error(f"Erro ao inspecionar fontes: {e}", exc_info=True)
            else:
                st.warning("Por favor, digite uma pergunta para inspecionar.")
    
    # ========== ABA: AJUDA ==========
    with tab_help:
        st.markdown("### 💡 Como Usar o Chatbot RAG")
        
        st.markdown("""
        #### 📖 Passo a Passo
        
        1. **Prepare seus documentos**
           - Adicione arquivos `.txt`, `.md`, `.pdf` ou `.docx` na pasta de dados (padrão: `./data/`)
           - Os documentos devem conter informações que você quer consultar
           - **Novidade v3.0:** Suporte para PDFs e DOCX!
        
        2. **Alimente o RAG**
           - Vá para a aba **"📚 Gerenciar RAG"**
           - Clique em **"🔄 Alimentar RAG"**
           - Aguarde o processamento dos documentos
           - **Novidade v3.0:** Divisão inteligente em chunks para melhor precisão!
        
        3. **Faça perguntas**
           - Vá para a aba **"💬 Chat"**
           - Digite sua pergunta no chat
           - **Novidade v3.0:** Envie imagens junto com sua pergunta (ex: gráficos, diagramas)
           - **Novidade v3.0:** Faça perguntas de acompanhamento - o chatbot lembra da conversa!
           - O sistema buscará informações relevantes e gerará uma resposta
        
        4. **Verifique as fontes**
           - Clique em **"Ver fontes utilizadas"** abaixo de cada resposta
           - Veja quais documentos/chunks foram usados para gerar a resposta
        
        #### 🖼️ Análise Multimodal
        
        **Novidade v3.0:** O chatbot agora pode analisar imagens!
        - Envie uma imagem usando o uploader na aba de Chat
        - O modelo multimodal (ex: llava) analisará a imagem junto com o contexto do RAG
        - Ideal para analisar gráficos, diagramas, capturas de tela, etc.
        
        #### 💬 Memória Conversacional
        
        **Novidade v3.0:** O chatbot lembra da conversa!
        - Faça perguntas de acompanhamento sem repetir o contexto
        - Exemplo: "E o segundo ponto que você mencionou?" funciona!
        - O histórico é preservado durante toda a sessão
        
        #### 🔍 Inspeção de Fontes
        
        Use a seção **"🔍 Inspecionar Fontes"** na aba **"Gerenciar RAG"** para:
        - Testar quais documentos/chunks seriam recuperados para uma pergunta
        - Verificar se o RAG está funcionando corretamente
        - Entender a qualidade da busca semântica
        - **Novidade v3.0:** Veja informações sobre chunks (índice e total)
        
        #### ⚙️ Configurações
        
        - **Modelo LLM**: Altere na sidebar (padrão: llama3)
        - **Modelo Multimodal**: Configurado como llava (para análise de imagens)
        - **Pasta de Dados**: Altere na sidebar (padrão: ./data)
        - **Chunk Size**: {CHUNK_SIZE} caracteres por chunk
        - **Chunk Overlap**: {CHUNK_OVERLAP} caracteres de sobreposição
        - **Persistência**: Os dados são salvos automaticamente em `{CHROMA_PERSIST_DIRECTORY}`
        
        #### 📋 Requisitos
        
        - **Ollama** instalado e rodando
        - Modelo de texto baixado: `ollama pull llama3` (ou outro modelo)
        - **Opcional:** Modelo multimodal para imagens: `ollama pull llava`
        - Documentos na pasta de dados (suporta .txt, .md, .pdf, .docx)
        
        #### 🐛 Troubleshooting
        
        - Se o chatbot não responder, verifique se o Ollama está rodando: `ollama serve`
        - Se nenhuma fonte for encontrada, certifique-se de ter alimentado o RAG
        - Para usar análise de imagens, certifique-se de ter o modelo llava instalado
        - Verifique os logs em `./logs/rag_chatbot.log` para detalhes
        
        #### 🆕 Novidades v3.0
        
        - ✂️ **Divisão inteligente de documentos** em chunks para maior precisão
        - 📄 **Suporte multi-formato:** PDFs e DOCX além de TXT e MD
        - 🖼️ **Análise multimodal:** Envie imagens junto com perguntas
        - 💬 **Memória conversacional:** Chatbot lembra do contexto da conversa
        - 🎯 **Rastreamento de chunks:** Veja de qual parte do documento vem cada resposta
        """)
        
        st.markdown("---")
        st.markdown("**💾 Persistência:** Os dados do RAG são salvos automaticamente e persistem entre reinicializações.")
        st.markdown(f"**📁 Diretório ChromaDB:** `{CHROMA_PERSIST_DIRECTORY}`")
    
    # Botão para limpar histórico na sidebar
    st.sidebar.markdown("---")
    if st.sidebar.button("🗑️ Limpar Histórico do Chat"):
        st.session_state.messages = []
        st.rerun()


if __name__ == "__main__":
    main()
