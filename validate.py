#!/usr/bin/env python
"""Script de validação da estrutura do sistema RAG."""

import sys
from pathlib import Path

def check_imports():
    """Verifica se as importações básicas funcionam."""
    print("🔍 Verificando estrutura do código...")
    
    try:
        # Verificar interfaces
        from rag_chatbot.interfaces import (
            IDocumentLoader, IEmbeddingModel, IVectorStore, ILocalLLM, Documento
        )
        print("✅ Interfaces importadas com sucesso")
        
        # Verificar core
        from rag_chatbot.core import RAGChatbot
        print("✅ Core (RAGChatbot) importado com sucesso")
        
        # Verificar config
        from rag_chatbot.config import DEFAULT_EMBEDDING_MODEL, DEFAULT_LLM_MODEL
        print(f"✅ Config importado (LLM: {DEFAULT_LLM_MODEL}, Embedder: {DEFAULT_EMBEDDING_MODEL})")
        
        # Verificar components
        from rag_chatbot.components.loaders import FolderLoader
        print("✅ FolderLoader importado")
        
        from rag_chatbot.components.llms import MockLLM
        print("✅ MockLLM importado")
        
        print("\n✨ Estrutura básica do código está correta!")
        return True
        
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def check_structure():
    """Verifica estrutura de pastas."""
    print("\n🔍 Verificando estrutura de pastas...")
    
    required_paths = [
        "rag_chatbot",
        "rag_chatbot/components",
        "tests",
        "app.py",
        "requirements.txt",
        "README.md",
    ]
    
    all_ok = True
    for path in required_paths:
        p = Path(path)
        if p.exists():
            print(f"✅ {path}")
        else:
            print(f"❌ {path} não encontrado")
            all_ok = False
    
    return all_ok

def check_data_folder():
    """Verifica se a pasta de dados existe."""
    print("\n🔍 Verificando pasta de dados...")
    
    data_path = Path("data")
    if data_path.exists():
        txt_files = list(data_path.glob("*.txt")) + list(data_path.glob("*.md"))
        print(f"✅ Pasta 'data' existe com {len(txt_files)} arquivo(s)")
        for f in txt_files:
            print(f"   📄 {f.name}")
        return True
    else:
        print("⚠️  Pasta 'data' não existe (será criada automaticamente)")
        return True

def main():
    """Executa todas as verificações."""
    print("=" * 60)
    print("🤖 Validação do Sistema RAG Chatbot")
    print("=" * 60)
    
    results = []
    
    results.append(("Estrutura de Pastas", check_structure()))
    results.append(("Importações Python", check_imports()))
    results.append(("Pasta de Dados", check_data_folder()))
    
    print("\n" + "=" * 60)
    print("📊 Resumo da Validação")
    print("=" * 60)
    
    for name, ok in results:
        status = "✅ OK" if ok else "❌ FALHOU"
        print(f"{name}: {status}")
    
    all_passed = all(ok for _, ok in results)
    
    if all_passed:
        print("\n✨ Sistema validado com sucesso!")
        print("\n📝 Próximos passos:")
        print("1. Instalar dependências: pip install -r requirements.txt")
        print("2. Instalar Ollama: https://ollama.com")
        print("3. Baixar modelo: ollama pull llama3")
        print("4. Executar: streamlit run app.py")
        return 0
    else:
        print("\n⚠️  Algumas verificações falharam.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
