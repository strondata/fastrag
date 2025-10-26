# 🏗️ Arquitetura do Sistema

## Visão Geral

O sistema RAG Chatbot foi desenvolvido seguindo os **princípios SOLID** e **Clean Architecture**, garantindo:

- ✅ Modularidade
- ✅ Testabilidade  
- ✅ Extensibilidade
- ✅ Manutenibilidade

## Diagrama de Componentes

```
┌─────────────────────────────────────────────────────────┐
│                    Streamlit UI (app.py)                 │
│                     Interface do Usuário                 │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│                RAGChatbot (core.py)                      │
│                   Orquestrador Principal                 │
│  ┌──────────────────────────────────────────────────┐  │
│  │  ingest_data() → ask() → get_sources()           │  │
│  └──────────────────────────────────────────────────┘  │
└───┬──────────┬───────────┬──────────┬─────────────────┘
    │          │           │          │
    ▼          ▼           ▼          ▼
┌────────┐ ┌────────┐ ┌─────────┐ ┌──────┐
│ Loader │ │Embedder│ │ Vector  │ │ LLM  │
│        │ │        │ │  Store  │ │      │
└────────┘ └────────┘ └─────────┘ └──────┘
    │          │           │          │
    ▼          ▼           ▼          ▼
┌────────┐ ┌────────┐ ┌─────────┐ ┌──────┐
│Folder  │ │MiniLM  │ │ Chroma  │ │Ollama│
│Loader  │ │Embedder│ │  Store  │ │ LLM  │
└────────┘ └────────┘ └─────────┘ └──────┘
```

## Camadas da Arquitetura

### 1. Interface Layer (UI)
**Arquivo**: `app.py`

- Interface Streamlit
- Gerenciamento de sessão
- Interação com usuário

### 2. Application Layer (Core)
**Arquivo**: `core.py`

- **RAGChatbot**: Orquestrador principal
- Coordena fluxo de dados
- Implementa lógica RAG

### 3. Domain Layer (Interfaces)
**Arquivo**: `interfaces.py`

Define contratos (abstrações):
- `IDocumentLoader`
- `IEmbeddingModel`
- `IVectorStore`
- `ILocalLLM`
- `Documento` (data class)

### 4. Infrastructure Layer (Components)
**Diretório**: `components/`

Implementações concretas:
- `loaders.py`: FolderLoader
- `embedders.py`: MiniLMEmbedder
- `vector_stores.py`: ChromaVectorStore
- `llms.py`: OllamaLLM, MockLLM

## Fluxo de Dados

### Fluxo de Ingestão

```
1. FolderLoader.load(path)
   └─> List[Documento]

2. MiniLMEmbedder.embed_documents(texts)
   └─> List[List[float]]

3. ChromaVectorStore.add(docs, embeddings)
   └─> Armazenamento persistente
```

### Fluxo de Query

```
1. Usuário faz pergunta
   └─> "Qual a cor do cachorro?"

2. MiniLMEmbedder.embed_query(question)
   └─> [0.123, 0.456, ...]

3. ChromaVectorStore.search(embedding, k=3)
   └─> Top 3 documentos relevantes

4. RAGChatbot constrói prompt
   └─> CONTEXTO + PERGUNTA

5. OllamaLLM.generate(prompt)
   └─> Resposta final
```

## Princípios SOLID Aplicados

### [S] Single Responsibility Principle

Cada classe tem **uma única responsabilidade**:

| Classe | Responsabilidade |
|--------|------------------|
| FolderLoader | Carregar arquivos |
| MiniLMEmbedder | Gerar embeddings |
| ChromaVectorStore | Armazenar/buscar vetores |
| OllamaLLM | Gerar texto |
| RAGChatbot | Orquestrar fluxo |

### [O] Open/Closed Principle

**Aberto para extensão**, fechado para modificação:

```python
# ✅ Adicionar novo loader SEM modificar código existente
class PDFLoader(IDocumentLoader):
    def load(self, source: str) -> List[Documento]:
        # Implementação específica
        pass

# Usar no sistema
chatbot = RAGChatbot(
    loader=PDFLoader(),  # Nova implementação
    embedder=embedder,
    store=store,
    llm=llm
)
```

### [L] Liskov Substitution Principle

Qualquer implementação pode substituir outra:

```python
# ✅ Todas essas combinações funcionam:
chatbot1 = RAGChatbot(loader1, embedder1, store1, llm1)
chatbot2 = RAGChatbot(loader2, embedder2, store2, llm2)
chatbot3 = RAGChatbot(loader1, embedder2, store1, llm2)
```

### [I] Interface Segregation Principle

Interfaces **pequenas e focadas**:

```python
# ✅ Cada interface tem métodos específicos
IDocumentLoader    → load()
IEmbeddingModel    → embed_documents(), embed_query()
IVectorStore       → add(), search()
ILocalLLM          → generate()
```

### [D] Dependency Inversion Principle

RAGChatbot depende de **abstrações**, não implementações:

```python
# ✅ Depende de interfaces
class RAGChatbot:
    def __init__(
        self,
        loader: IDocumentLoader,      # Interface
        embedder: IEmbeddingModel,    # Interface
        store: IVectorStore,          # Interface
        llm: ILocalLLM               # Interface
    ):
        # ...
```

## Padrões de Design Utilizados

### 1. Dependency Injection

Componentes são **injetados** no construtor:

```python
chatbot = RAGChatbot(
    loader=FolderLoader(),
    embedder=MiniLMEmbedder(),
    store=ChromaVectorStore(),
    llm=OllamaLLM()
)
```

### 2. Strategy Pattern

Diferentes estratégias (implementações) intercambiáveis:

```python
# Estratégia 1: Ollama
chatbot1 = RAGChatbot(..., llm=OllamaLLM())

# Estratégia 2: Mock (para testes)
chatbot2 = RAGChatbot(..., llm=MockLLM())
```

### 3. Template Method

RAGChatbot define o **esqueleto** do algoritmo RAG:

```python
def ask(self, question):
    # 1. Embedar query
    embedding = self.embedder.embed_query(question)
    
    # 2. Buscar contexto
    docs = self.vector_store.search(embedding, k=3)
    
    # 3. Construir prompt
    prompt = self.prompt_template.format(...)
    
    # 4. Gerar resposta
    return self.llm.generate(prompt)
```

## Testabilidade

### Unit Tests com Mocks

```python
# Testar RAGChatbot isoladamente
def test_ask():
    mock_embedder = Mock()
    mock_store = Mock()
    mock_llm = Mock()
    
    chatbot = RAGChatbot(
        loader=...,
        embedder=mock_embedder,
        store=mock_store,
        llm=mock_llm
    )
    
    chatbot.ask("Teste")
    
    mock_llm.generate.assert_called_once()
```

### Integration Tests

```python
# Testar fluxo completo
def test_full_flow():
    chatbot = RAGChatbot(
        loader=FolderLoader(),
        embedder=MiniLMEmbedder(),
        store=ChromaVectorStore(),
        llm=MockLLM()
    )
    
    chatbot.ingest_data("./test_data")
    response = chatbot.ask("Pergunta")
    
    assert response is not None
```

## Extensibilidade

### Adicionar Novo Loader

```python
class APILoader(IDocumentLoader):
    def load(self, source: str) -> List[Documento]:
        response = requests.get(source)
        data = response.json()
        return [Documento(content=d['text'], metadata=d) for d in data]
```

### Adicionar Novo Vector Store

```python
class FAISSVectorStore(IVectorStore):
    def __init__(self):
        self.index = faiss.IndexFlatL2(384)
    
    def add(self, documents, embeddings):
        # Implementação FAISS
        pass
    
    def search(self, query_embedding, k):
        # Busca FAISS
        pass
```

### Adicionar Novo LLM

```python
class OpenAILLM(ILocalLLM):
    def generate(self, prompt: str) -> str:
        response = openai.ChatCompletion.create(...)
        return response.choices[0].message.content
```

## Logging e Observabilidade

```python
# Configuração centralizada
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/rag_chatbot.log"),
        logging.StreamHandler()
    ]
)

# Logs em todos os componentes
logger.info("Iniciando ingestão...")
logger.debug(f"Documento carregado: {filename}")
logger.error(f"Erro ao processar: {e}")
```

## Configuração

Configurações centralizadas em `config.py`:

```python
DEFAULT_EMBEDDING_MODEL = "all-MiniLM-L6-v2"
DEFAULT_LLM_MODEL = "llama3"
DEFAULT_COLLECTION_NAME = "rag_store"
DEFAULT_TOP_K = 3
```

## Segurança

- ✅ Dados locais (sem envio para cloud)
- ✅ LLM local (Ollama)
- ✅ Sem API keys necessárias
- ✅ Controle total dos dados

## Performance

### Otimizações

1. **Caching** (Streamlit):
   ```python
   @st.cache_resource
   def inicializar_chatbot():
       # Carrega modelos uma vez
   ```

2. **Batch Processing**:
   ```python
   embeddings = embedder.embed_documents(all_texts)
   ```

3. **ChromaDB** índice eficiente

## Conclusão

Esta arquitetura permite:

- ✅ **Testes** fáceis (mocks)
- ✅ **Manutenção** simples (responsabilidades separadas)
- ✅ **Extensão** sem modificar código existente
- ✅ **Substituição** de componentes (interfaces)
- ✅ **Evolução** do sistema

---

**Próximos Passos de Evolução**:
1. Suporte a PDF/DOCX
2. Chunking de documentos grandes
3. Re-ranking de resultados
4. Streaming de respostas
5. Histórico de conversas
