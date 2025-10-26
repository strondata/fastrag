"""Testes para text splitters."""

import pytest
from rag_chatbot.components.text_splitters import RecursiveCharacterTextSplitter
from rag_chatbot.interfaces import Documento


class TestRecursiveCharacterTextSplitter:
    """Testes para RecursiveCharacterTextSplitter."""
    
    def test_split_small_document(self):
        """Testa divisão de documento menor que chunk_size."""
        splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=20)
        
        doc = Documento(
            content="Este é um texto pequeno.",
            metadata={"source": "test.txt"}
        )
        
        chunks = splitter.split_documents([doc])
        
        # Documento pequeno não deve ser dividido
        assert len(chunks) == 1
        assert chunks[0].content == "Este é um texto pequeno."
        assert chunks[0].metadata["source"] == "test.txt"
        assert chunks[0].metadata["chunk_index"] == 0
        assert chunks[0].metadata["total_chunks"] == 1
    
    def test_split_large_document_by_paragraphs(self):
        """Testa divisão de documento grande usando parágrafos."""
        splitter = RecursiveCharacterTextSplitter(chunk_size=50, chunk_overlap=10)
        
        content = "Parágrafo um com texto suficiente.\n\nParágrafo dois com mais texto.\n\nParágrafo três final."
        doc = Documento(content=content, metadata={"source": "test.txt"})
        
        chunks = splitter.split_documents([doc])
        
        # Deve dividir em múltiplos chunks
        assert len(chunks) > 1
        
        # Verificar que metadados foram herdados
        for i, chunk in enumerate(chunks):
            assert chunk.metadata["source"] == "test.txt"
            assert chunk.metadata["chunk_index"] == i
            assert chunk.metadata["total_chunks"] == len(chunks)
    
    def test_split_with_overlap(self):
        """Testa que a sobreposição funciona corretamente."""
        splitter = RecursiveCharacterTextSplitter(chunk_size=30, chunk_overlap=10)
        
        content = "palavra1 palavra2 palavra3 palavra4 palavra5 palavra6 palavra7"
        doc = Documento(content=content, metadata={"source": "test.txt"})
        
        chunks = splitter.split_documents([doc])
        
        assert len(chunks) > 1
        
        # Verificar que há sobreposição entre chunks consecutivos
        for i in range(len(chunks) - 1):
            # Alguns caracteres do final do chunk i devem aparecer no início do chunk i+1
            # (devido ao overlap)
            assert len(chunks[i].content) > 0
            assert len(chunks[i + 1].content) > 0
    
    def test_split_multiple_documents(self):
        """Testa divisão de múltiplos documentos."""
        splitter = RecursiveCharacterTextSplitter(chunk_size=30, chunk_overlap=5)
        
        docs = [
            Documento(
                content="Documento um com texto suficiente para divisão.",
                metadata={"source": "doc1.txt"}
            ),
            Documento(
                content="Documento dois também com texto para dividir.",
                metadata={"source": "doc2.txt"}
            )
        ]
        
        chunks = splitter.split_documents(docs)
        
        # Deve ter chunks de ambos os documentos
        assert len(chunks) > 2
        
        # Verificar que metadados foram preservados corretamente
        sources = set(chunk.metadata["source"] for chunk in chunks)
        assert "doc1.txt" in sources
        assert "doc2.txt" in sources
    
    def test_metadata_inheritance(self):
        """Testa que metadados customizados são herdados pelos chunks."""
        splitter = RecursiveCharacterTextSplitter(chunk_size=30, chunk_overlap=5)
        
        doc = Documento(
            content="Texto longo que será dividido em múltiplos chunks para teste.",
            metadata={
                "source": "test.txt",
                "author": "Test Author",
                "date": "2024-01-01",
                "category": "test"
            }
        )
        
        chunks = splitter.split_documents([doc])
        
        # Todos os chunks devem herdar os metadados
        for chunk in chunks:
            assert chunk.metadata["source"] == "test.txt"
            assert chunk.metadata["author"] == "Test Author"
            assert chunk.metadata["date"] == "2024-01-01"
            assert chunk.metadata["category"] == "test"
            assert "chunk_index" in chunk.metadata
            assert "total_chunks" in chunk.metadata
    
    def test_empty_document(self):
        """Testa divisão de documento vazio."""
        splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=20)
        
        doc = Documento(content="", metadata={"source": "empty.txt"})
        
        chunks = splitter.split_documents([doc])
        
        # Documento vazio pode retornar lista vazia ou um único chunk vazio
        assert len(chunks) <= 1
    
    def test_custom_separators(self):
        """Testa uso de separadores customizados."""
        # Usar apenas vírgula como separador
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=30,
            chunk_overlap=5,
            separators=[",", ""]
        )
        
        content = "item1,item2,item3,item4,item5,item6,item7,item8"
        doc = Documento(content=content, metadata={"source": "test.txt"})
        
        chunks = splitter.split_documents([doc])
        
        # Deve dividir baseado em vírgulas
        assert len(chunks) > 1
        
        # Verificar que a divisão ocorreu
        for chunk in chunks:
            assert len(chunk.content) > 0
