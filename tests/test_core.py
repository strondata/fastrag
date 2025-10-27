"""Testes unitários para o módulo core (RAGChatbot)."""

import pytest
from unittest.mock import Mock, MagicMock

from src.rag_chatbot.core import RAGChatbot
from src.rag_chatbot.interfaces import Documento


class TestRAGChatbot:
    """Testes para a classe RAGChatbot."""
    
    @pytest.fixture
    def mock_components(self):
        """Cria mocks para todos os componentes."""
        mock_loader = Mock()
        mock_embedder = Mock()
        mock_store = Mock()
        mock_llm = Mock()
        
        return {
            'loader': mock_loader,
            'embedder': mock_embedder,
            'store': mock_store,
            'llm': mock_llm
        }
    
    @pytest.fixture
    def chatbot(self, mock_components):
        """Cria uma instância do RAGChatbot com mocks."""
        return RAGChatbot(
            loader=mock_components['loader'],
            embedder=mock_components['embedder'],
            store=mock_components['store'],
            llm=mock_components['llm']
        )
    
    def test_ingest_data_success(self, chatbot, mock_components):
        """Testa ingestão bem-sucedida de dados."""
        # Configurar mocks
        test_docs = [
            Documento(content="Teste 1", metadata={"source": "test1.txt"}),
            Documento(content="Teste 2", metadata={"source": "test2.txt"})
        ]
        
        mock_components['loader'].load.return_value = test_docs
        mock_components['embedder'].embed_documents.return_value = [[0.1, 0.2], [0.3, 0.4]]
        
        # Executar
        num_docs = chatbot.ingest_data("/fake/path")
        
        # Verificar
        assert num_docs == 2
        mock_components['loader'].load.assert_called_once_with("/fake/path")
        mock_components['embedder'].embed_documents.assert_called_once()
        mock_components['store'].add.assert_called_once()
    
    def test_ingest_data_no_documents(self, chatbot, mock_components):
        """Testa ingestão quando não há documentos."""
        mock_components['loader'].load.return_value = []
        
        num_docs = chatbot.ingest_data("/fake/path")
        
        assert num_docs == 0
        mock_components['embedder'].embed_documents.assert_not_called()
        mock_components['store'].add.assert_not_called()
    
    def test_ask_with_context(self, chatbot, mock_components):
        """Testa geração de resposta com contexto."""
        # Configurar mocks
        mock_components['embedder'].embed_query.return_value = [0.5, 0.6]
        
        context_docs = [
            Documento(content="O cachorro é marrom", metadata={"source": "test.txt"})
        ]
        mock_components['store'].search.return_value = context_docs
        mock_components['llm'].generate.return_value = "O cachorro é marrom."
        
        # Executar
        response = chatbot.ask("Qual a cor do cachorro?")
        
        # Verificar
        assert response == "O cachorro é marrom."
        mock_components['embedder'].embed_query.assert_called_once_with("Qual a cor do cachorro?")
        mock_components['store'].search.assert_called_once()
        
        # Verificar que o prompt contém o contexto
        call_args = mock_components['llm'].generate.call_args
        prompt = call_args[0][0]
        assert "O cachorro é marrom" in prompt
        assert "Qual a cor do cachorro?" in prompt
    
    def test_ask_without_context(self, chatbot, mock_components):
        """Testa geração de resposta sem contexto disponível."""
        mock_components['embedder'].embed_query.return_value = [0.5, 0.6]
        mock_components['store'].search.return_value = []
        mock_components['llm'].generate.return_value = "Não sei."
        
        response = chatbot.ask("Pergunta aleatória?")
        
        assert response == "Não sei."
        
        # Verificar que o prompt contém mensagem de contexto vazio
        call_args = mock_components['llm'].generate.call_args
        prompt = call_args[0][0]
        assert "Nenhuma informação disponível" in prompt
    
    def test_get_sources(self, chatbot, mock_components):
        """Testa recuperação de documentos fonte."""
        mock_components['embedder'].embed_query.return_value = [0.5, 0.6]
        
        expected_docs = [
            Documento(content="Doc 1", metadata={"source": "1.txt"}),
            Documento(content="Doc 2", metadata={"source": "2.txt"})
        ]
        mock_components['store'].search.return_value = expected_docs
        
        sources = chatbot.get_sources("Teste", k=2)
        
        assert len(sources) == 2
        assert sources == expected_docs
        mock_components['store'].search.assert_called_once_with([0.5, 0.6], k=2)
    
    def test_ask_with_image(self, chatbot, mock_components):
        """Testa geração de resposta com imagem."""
        # Configurar mocks
        mock_components['embedder'].embed_query.return_value = [0.5, 0.6]
        mock_components['store'].search.return_value = []
        mock_components['llm'].generate.return_value = "Resposta multimodal."
        
        # Executar com dados de imagem
        image_data = b"fake_image_data"
        response = chatbot.ask("Pergunta com imagem", image_data=image_data)
        
        # Verificar
        assert response == "Resposta multimodal."
        
        # Verificar que generate foi chamado com images_base64
        call_args = mock_components['llm'].generate.call_args
        assert call_args[1]['images_base64'] is not None
        assert len(call_args[1]['images_base64']) == 1
    
    def test_ask_with_chat_history(self, chatbot, mock_components):
        """Testa geração de resposta com histórico de conversa."""
        # Configurar mocks
        mock_components['embedder'].embed_query.return_value = [0.5, 0.6]
        
        context_docs = [
            Documento(content="Contexto relevante", metadata={"source": "test.txt"})
        ]
        mock_components['store'].search.return_value = context_docs
        mock_components['llm'].generate.return_value = "Resposta com histórico."
        
        # Criar histórico de chat
        chat_history = [
            {"role": "user", "content": "Primeira pergunta"},
            {"role": "assistant", "content": "Primeira resposta"}
        ]
        
        # Executar
        response = chatbot.ask("Segunda pergunta", chat_history=chat_history)
        
        # Verificar
        assert response == "Resposta com histórico."
        
        # Verificar que o prompt contém o histórico
        call_args = mock_components['llm'].generate.call_args
        prompt = call_args[0][0]
        assert "Primeira pergunta" in prompt
        assert "Primeira resposta" in prompt
        assert "Segunda pergunta" in prompt
        assert "HISTÓRICO" in prompt
    
    def test_ingest_with_text_splitter(self, mock_components):
        """Testa ingestão com text splitter."""
        from unittest.mock import Mock
        
        # Criar mock text splitter
        mock_splitter = Mock()
        
        # Criar chatbot com text splitter
        chatbot_with_splitter = RAGChatbot(
            loader=mock_components['loader'],
            embedder=mock_components['embedder'],
            store=mock_components['store'],
            llm=mock_components['llm'],
            text_splitter=mock_splitter
        )
        
        # Configurar mocks
        original_docs = [
            Documento(content="Documento grande", metadata={"source": "test.txt"})
        ]
        
        split_docs = [
            Documento(content="Chunk 1", metadata={"source": "test.txt", "chunk_index": 0}),
            Documento(content="Chunk 2", metadata={"source": "test.txt", "chunk_index": 1})
        ]
        
        mock_components['loader'].load.return_value = original_docs
        mock_splitter.split_documents.return_value = split_docs
        mock_components['embedder'].embed_documents.return_value = [[0.1, 0.2], [0.3, 0.4]]
        
        # Executar
        num_docs = chatbot_with_splitter.ingest_data("/fake/path")
        
        # Verificar
        assert num_docs == 2  # Número de chunks, não documentos originais
        mock_splitter.split_documents.assert_called_once_with(original_docs)
        mock_components['embedder'].embed_documents.assert_called_once()
        mock_components['store'].add.assert_called_once()
