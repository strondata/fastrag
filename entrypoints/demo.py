#!/usr/bin/env python
"""Script de demonstração do RAG Chatbot (sem necessidade de Ollama).

Este script demonstra o funcionamento do sistema RAG usando MockLLM,
que não requer Ollama instalado.
"""

from src.rag_chatbot.core import RAGChatbot
from src.rag_chatbot.components.loaders import FolderLoader
from src.rag_chatbot.components.llms import MockLLM
from src.rag_chatbot.interfaces import IEmbeddingModel, IVectorStore, Documento
from typing import List


class SimpleEmbedder(IEmbeddingModel):
    """Embedder simples para demonstração (não usa ML real)."""
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        # Retorna embeddings fictícios baseados no comprimento
        return [[float(len(text)), float(text.count(' '))] for text in texts]
    
    def embed_query(self, text: str) -> List[float]:
        return [float(len(text)), float(text.count(' '))]


class SimpleVectorStore(IVectorStore):
    """Vector store simples para demonstração (busca por palavra-chave)."""
    
    def __init__(self):
        self.documents = []
    
    def add(self, documents: List[Documento], embeddings: List[List[float]]) -> None:
        self.documents.extend(documents)
    
    def search(self, query_embedding: List[float], k: int) -> List[Documento]:
        # Retorna todos os documentos (busca simples)
        return self.documents[:k]


def main():
    """Demonstração do sistema."""
    print("=" * 60)
    print("🤖 Demonstração do Sistema RAG Chatbot")
    print("=" * 60)
    print()
    
    # Criar componentes simples
    print("📦 Inicializando componentes...")
    loader = FolderLoader()
    embedder = SimpleEmbedder()
    store = SimpleVectorStore()
    llm = MockLLM(default_response="Esta é uma resposta de demonstração. Em produção, usaria Ollama.")
    
    # Criar chatbot
    chatbot = RAGChatbot(loader, embedder, store, llm)
    print("✅ Chatbot criado!")
    print()
    
    # Ingerir dados
    print("📚 Carregando base de conhecimento...")
    data_path = "./data"
    num_docs = chatbot.ingest_data(data_path)
    print(f"✅ {num_docs} documento(s) carregado(s)")
    print()
    
    # Fazer algumas perguntas
    questions = [
        "O que é este sistema?",
        "Quais são as características principais?",
        "Como usar o chatbot?"
    ]
    
    print("💬 Demonstrando perguntas e respostas:")
    print("-" * 60)
    
    for i, question in enumerate(questions, 1):
        print(f"\n[Pergunta {i}]: {question}")
        
        # Obter fontes
        sources = chatbot.get_sources(question, k=1)
        if sources:
            print(f"[Fonte]: {sources[0].metadata.get('source', 'N/A')}")
            print(f"[Contexto]: {sources[0].content[:100]}...")
        
        # Obter resposta
        response = chatbot.ask(question)
        print(f"[Resposta]: {response}")
    
    print()
    print("-" * 60)
    print()
    print("✨ Demonstração concluída!")
    print()
    print("📝 Nota: Este exemplo usa MockLLM para demonstração.")
    print("   Para usar um LLM real, instale Ollama e use OllamaLLM.")
    print()
    print("🚀 Para interface completa, execute: streamlit run app.py")
    print()


if __name__ == "__main__":
    main()
