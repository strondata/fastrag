"""Testes unitários para o módulo core (RAGChatbot)."""

import pytest
from unittest.mock import Mock, MagicMock

from rag_chatbot.core import RAGChatbot
from rag_chatbot.interfaces import Documento


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
