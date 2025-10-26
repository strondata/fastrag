"""Testes para os componentes concretos."""

import pytest
import tempfile
import shutil
from pathlib import Path

from rag_chatbot.components.loaders import FolderLoader
from rag_chatbot.components.embedders import MiniLMEmbedder
from rag_chatbot.components.vector_stores import ChromaVectorStore
from rag_chatbot.components.llms import MockLLM
from rag_chatbot.interfaces import Documento


class TestFolderLoader:
    """Testes para FolderLoader."""
    
    @pytest.fixture
    def temp_data_dir(self):
        """Cria um diretório temporário com arquivos de teste."""
        temp_dir = tempfile.mkdtemp()
        
        # Criar arquivos de teste
        (Path(temp_dir) / "test1.txt").write_text("Conteúdo do arquivo 1", encoding='utf-8')
        (Path(temp_dir) / "test2.txt").write_text("Conteúdo do arquivo 2", encoding='utf-8')
        (Path(temp_dir) / "test3.md").write_text("# Markdown\nConteúdo markdown", encoding='utf-8')
        
        yield temp_dir
        
        # Limpar
        shutil.rmtree(temp_dir)
    
    def test_load_txt_files(self, temp_data_dir):
        """Testa carregamento de arquivos .txt."""
        loader = FolderLoader()
        documents = loader.load(temp_data_dir)
        
        assert len(documents) == 3  # 2 .txt + 1 .md
        
        # Verificar conteúdos
        contents = [doc.content for doc in documents]
        assert "Conteúdo do arquivo 1" in contents
        assert "Conteúdo do arquivo 2" in contents
        
        # Verificar metadados
        assert all('source' in doc.metadata for doc in documents)
        assert all('path' in doc.metadata for doc in documents)
    
    def test_load_empty_directory(self):
        """Testa carregamento de diretório vazio."""
        with tempfile.TemporaryDirectory() as temp_dir:
            loader = FolderLoader()
            documents = loader.load(temp_dir)
            
            assert len(documents) == 0


class TestMiniLMEmbedder:
    """Testes para MiniLMEmbedder."""
    
    @pytest.fixture
    def embedder(self):
        """Cria uma instância do embedder."""
        return MiniLMEmbedder()
    
    def test_embed_documents(self, embedder):
        """Testa geração de embeddings para documentos."""
        texts = ["Texto 1", "Texto 2", "Texto 3"]
        embeddings = embedder.embed_documents(texts)
        
        assert len(embeddings) == 3
        assert all(isinstance(emb, list) for emb in embeddings)
        assert all(len(emb) > 0 for emb in embeddings)
        assert all(isinstance(val, float) for emb in embeddings for val in emb)
    
    def test_embed_query(self, embedder):
        """Testa geração de embedding para uma query."""
        query = "Qual é a resposta?"
        embedding = embedder.embed_query(query)
        
        assert isinstance(embedding, list)
        assert len(embedding) > 0
        assert all(isinstance(val, float) for val in embedding)
    
    def test_embeddings_consistency(self, embedder):
        """Testa que textos iguais geram embeddings iguais."""
        text = "Texto de teste"
        emb1 = embedder.embed_query(text)
        emb2 = embedder.embed_query(text)
        
        assert emb1 == emb2


class TestChromaVectorStore:
    """Testes para ChromaVectorStore."""
    
    @pytest.fixture
    def store(self):
        """Cria uma instância in-memory do vector store."""
        return ChromaVectorStore(collection_name="test_collection")
    
    def test_add_and_search(self, store):
        """Testa adição e busca de documentos."""
        # Criar documentos de teste
        docs = [
            Documento(content="O gato é preto", metadata={"source": "1.txt"}),
            Documento(content="O cachorro é branco", metadata={"source": "2.txt"}),
            Documento(content="O pássaro é azul", metadata={"source": "3.txt"})
        ]
        
        # Embeddings fictícios (normalmente viriam do embedder)
        embeddings = [
            [0.1, 0.2, 0.3],
            [0.4, 0.5, 0.6],
            [0.7, 0.8, 0.9]
        ]
        
        # Adicionar
        store.add(docs, embeddings)
        
        # Buscar (usando embedding similar ao primeiro)
        results = store.search([0.1, 0.2, 0.3], k=2)
        
        assert len(results) <= 2
        assert all(isinstance(doc, Documento) for doc in results)
    
    def test_add_empty_documents(self, store):
        """Testa adição de lista vazia."""
        store.add([], [])
        # Não deve causar erro
    
    def test_search_empty_store(self, store):
        """Testa busca em store vazio."""
        results = store.search([0.1, 0.2, 0.3], k=5)
        
        assert len(results) == 0


class TestMockLLM:
    """Testes para MockLLM."""
    
    def test_generate_default_response(self):
        """Testa geração com resposta padrão."""
        llm = MockLLM()
        response = llm.generate("Qualquer prompt")
        
        assert response == "Esta é uma resposta mock do LLM."
    
    def test_generate_custom_response(self):
        """Testa geração com resposta customizada."""
        custom_response = "Resposta personalizada"
        llm = MockLLM(default_response=custom_response)
        response = llm.generate("Qualquer prompt")
        
        assert response == custom_response


class TestIntegration:
    """Testes de integração do fluxo completo."""
    
    @pytest.fixture
    def temp_data_dir(self):
        """Cria um diretório temporário com dados de teste."""
        temp_dir = tempfile.mkdtemp()
        
        # Criar arquivo com informação específica
        (Path(temp_dir) / "animal.txt").write_text(
            "O cachorro é marrom e gosta de brincar.",
            encoding='utf-8'
        )
        
        yield temp_dir
        
        shutil.rmtree(temp_dir)
    
    def test_full_rag_flow(self, temp_data_dir):
        """Testa o fluxo completo: carregar -> embedar -> armazenar -> buscar."""
        from rag_chatbot.core import RAGChatbot
        
        # Componentes reais (exceto LLM que usa mock)
        loader = FolderLoader()
        embedder = MiniLMEmbedder()
        store = ChromaVectorStore(collection_name="integration_test")
        llm = MockLLM(default_response="O cachorro é marrom.")
        
        # Criar chatbot
        chatbot = RAGChatbot(loader, embedder, store, llm)
        
        # Ingestão
        num_docs = chatbot.ingest_data(temp_data_dir)
        assert num_docs == 1
        
        # Fazer pergunta
        response = chatbot.ask("Qual a cor do cachorro?")
        assert response == "O cachorro é marrom."
        
        # Verificar fontes
        sources = chatbot.get_sources("Qual a cor do cachorro?", k=1)
        assert len(sources) == 1
        assert "marrom" in sources[0].content
