# 🚀 Guia Rápido de Uso

## Instalação Rápida

```bash
# 1. Clonar repositório
git clone https://github.com/strondata/fastrag.git
cd fastrag

# 2. Criar ambiente virtual (recomendado)
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. Instalar dependências
pip install -r requirements.txt
```

## Configuração do Ollama

### Linux/Mac
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3
ollama serve
```

### Windows
1. Baixar de [ollama.com](https://ollama.com)
2. Instalar
3. Executar: `ollama pull llama3`

## Uso Básico

### 1. Adicionar Documentos

Crie ou adicione seus arquivos `.txt` ou `.md` na pasta `data/`:

```bash
mkdir -p data
echo "Python é uma linguagem de programação." > data/python.txt
echo "O Brasil é um país da América do Sul." > data/brasil.txt
```

### 2. Executar o Chatbot

```bash
streamlit run app.py
```

### 3. Usar a Interface Web

1. Abrir navegador em `http://localhost:8501`
2. Na sidebar, clicar em **"Alimentar RAG"**
3. Fazer perguntas no chat!

## Exemplo de Uso

**Você**: O que é Python?

**Bot**: Python é uma linguagem de programação de alto nível, conhecida por sua sintaxe clara e legibilidade...

## Demonstração sem Ollama

Se você quiser apenas ver o sistema funcionando sem instalar Ollama:

```bash
python demo.py
```

Este script usa um MockLLM e demonstra o fluxo completo.

## Validação da Instalação

```bash
python validate.py
```

## Estrutura de Dados

Os documentos são carregados de `./data/`:

```
data/
├── documento1.txt
├── documento2.txt
└── notas.md
```

## Personalização

### Alterar Modelo LLM

No Streamlit, edite o campo "Modelo LLM (Ollama)" na sidebar.

### Alterar Número de Resultados (k)

No código:
```python
response = chatbot.ask("Pergunta", k=5)  # Busca top 5 documentos
```

### Template de Prompt Customizado

```python
custom_template = """
Responda em português formal:
CONTEXTO: {context}
PERGUNTA: {question}
RESPOSTA:
"""

chatbot = RAGChatbot(..., prompt_template=custom_template)
```

## Troubleshooting

### Erro: "Ollama não está rodando"
```bash
ollama serve
```

### Erro: "Modelo não encontrado"
```bash
ollama pull llama3
```

### Erro: Módulo não encontrado
```bash
pip install -r requirements.txt
```

### Verificar Logs
```bash
cat logs/rag_chatbot.log
```

## Testes

```bash
# Todos os testes
pytest

# Com verbosidade
pytest -v

# Teste específico
pytest tests/test_core.py
```

## Recursos Avançados

### Usar ChromaDB Persistente

```python
from rag_chatbot.components.vector_stores import ChromaVectorStore

store = ChromaVectorStore(
    collection_name="meu_rag",
    persist_directory="./chroma_data"
)
```

### Criar Loader Customizado

```python
from rag_chatbot.interfaces import IDocumentLoader, Documento

class PDFLoader(IDocumentLoader):
    def load(self, source: str) -> List[Documento]:
        # Implementar leitura de PDF
        pass
```

### Múltiplas Fontes

```python
# Ingerir de várias pastas
chatbot.ingest_data("./data/docs")
chatbot.ingest_data("./data/articles")
chatbot.ingest_data("./data/notes")
```

## Próximos Passos

1. ✅ Adicione seus documentos em `./data/`
2. ✅ Inicie o Ollama
3. ✅ Execute `streamlit run app.py`
4. ✅ Comece a fazer perguntas!

## Suporte

- 📖 Documentação completa: [README.md](README.md)
- 🐛 Issues: GitHub Issues
- 💡 Exemplos: `demo.py`, `validate.py`

---

**Dica**: Comece com documentos pequenos para testar e depois expanda sua base de conhecimento!
