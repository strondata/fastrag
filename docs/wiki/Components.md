# Components Reference

Detailed documentation for all FastRAG components.

## Core Components

### Document Loaders

#### UniversalLoader

Loads documents from multiple file formats.

**Supported Formats**:
- `.txt` - Plain text
- `.md` - Markdown
- `.pdf` - PDF documents
- `.docx` - Word documents

**Usage**:
```python
from rag_chatbot.components.loaders import UniversalLoader

loader = UniversalLoader()
documents = loader.load("./data")
```

**API**:
```python
def load(source: str) -> List[Documento]:
    """
    Load documents from directory or file.
    
    Args:
        source: Path to directory or file
        
    Returns:
        List of Documento objects
    """
```

### Embedding Models

#### MiniLMEmbedder

Uses SentenceTransformers for text embeddings.

**Default Model**: `all-MiniLM-L6-v2` (384 dimensions)

**Usage**:
```python
from rag_chatbot.components.embedders import MiniLMEmbedder

embedder = MiniLMEmbedder()
# Or custom model:
embedder = MiniLMEmbedder(model_name="paraphrase-multilingual-MiniLM-L12-v2")

# Embed documents
embeddings = embedder.embed_documents(["text1", "text2"])

# Embed query
query_emb = embedder.embed_query("search query")
```

**API**:
```python
def embed_documents(texts: List[str]) -> List[List[float]]:
    """Embed multiple documents."""

def embed_query(text: str) -> List[float]:
    """Embed single query."""
```

### Vector Stores

#### ChromaVectorStore

ChromaDB-based persistent vector storage.

**Usage**:
```python
from rag_chatbot.components.vector_stores import ChromaVectorStore

store = ChromaVectorStore(
    collection_name="my_collection",
    persist_directory="./chroma_data"
)

# Add documents
store.add(documents, embeddings)

# Search
results = store.search(query_embedding, k=5)
```

**API**:
```python
def add(documents: List[Documento], embeddings: List[List[float]]):
    """Add documents with embeddings."""

def search(query_embedding: List[float], k: int) -> List[Documento]:
    """Search for k most similar documents."""
```

**Features**:
- Persistent storage
- Automatic deduplication (upsert)
- Metadata filtering
- Distance metrics

### LLM Models

#### OllamaLLM

Integrates with Ollama for local LLM inference.

**Usage**:
```python
from rag_chatbot.components.llms import OllamaLLM

llm = OllamaLLM(model_name="llama3")

# Generate text
response = llm.generate("What is Python?")

# With images (multimodal)
llm = OllamaLLM(multimodal_model_name="llava")
response = llm.generate(
    "Describe this image",
    images_base64=["base64_encoded_image"]
)
```

**API**:
```python
def generate(prompt: str, images_base64: List[str] = None) -> str:
    """Generate text from prompt."""
```

**Supported Models**:
- llama3, llama2
- mistral, mixtral
- phi, gemma
- llava (multimodal)
- codellama (code generation)

#### MockLLM

Mock LLM for testing without Ollama.

**Usage**:
```python
from rag_chatbot.components.llms import MockLLM

llm = MockLLM(default_response="Test response")
response = llm.generate("any prompt")  # Returns "Test response"
```

### Text Splitters

#### RecursiveCharacterTextSplitter

Splits text into chunks with overlap.

**Usage**:
```python
from rag_chatbot.components.text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

chunks = splitter.split_documents(documents)
```

**Features**:
- Recursive splitting (paragraphs → sentences → words)
- Customizable separators
- Overlap for context continuity
- Metadata inheritance

## Advanced Components

### Retrieval

#### BM25Retriever

Lexical retrieval using BM25 algorithm.

**Usage**:
```python
from rag_chatbot.retrieval import BM25Retriever

retriever = BM25Retriever(documents=documents)
results = retriever.retrieve("query")
```

#### VectorRetriever

Semantic retrieval using vector similarity.

**Usage**:
```python
from rag_chatbot.retrieval import VectorRetriever

retriever = VectorRetriever(
    vector_store=store,
    embedder=embedder
)
results = retriever.retrieve("query", top_k=5)
```

#### HybridRetriever

Combines BM25 and vector retrieval with RRF (Reciprocal Rank Fusion).

**Usage**:
```python
from rag_chatbot.retrieval import HybridRetriever

hybrid = HybridRetriever(
    vector_retriever=vector_ret,
    bm25_retriever=bm25_ret
)
results = hybrid.retrieve("query")
```

### Reranking

#### CrossEncoderReRanker

Reranks results using cross-encoder model.

**Usage**:
```python
from rag_chatbot.reranking import CrossEncoderReRanker

reranker = CrossEncoderReRanker()
reranked = reranker.rerank("query", documents, top_k=3)
```

### Query Transformation

#### QueryTransformer

Transforms queries for better retrieval.

**Strategies**:
- Query expansion
- Query decomposition
- Query rewriting

**Usage**:
```python
from rag_chatbot.query_transform import QueryTransformer

transformer = QueryTransformer(llm=llm)
expanded = transformer.expand_multi("What is RAG?")
```

### Context Compression

#### PromptCompressor

Compresses context to fit LLM limits.

**Usage**:
```python
from rag_chatbot.compression import PromptCompressor

compressor = PromptCompressor(llm=llm)
compressed = compressor.compress(documents, query="question")
```

### Memory

#### MemoryStream

Long-term memory with importance scoring.

**Usage**:
```python
from rag_chatbot.memory import MemoryStream

memory = MemoryStream(
    embedder=embedder,
    vector_store=store,
    llm=llm
)

# Add memory
memory.add_memory("Important fact", importance=8.5)

# Retrieve relevant memories
memories = memory.retrieve_relevant("query", k=3)
```

### Agents

#### Agent

ReAct-style reasoning agent with tool use.

**Usage**:
```python
from rag_chatbot.agent import Agent
from rag_chatbot.tools import CalculatorTool, RAGTool

tools = [CalculatorTool(), RAGTool(rag_pipeline=pipeline)]

agent = Agent(
    llm=llm,
    tools=tools,
    max_iterations=5
)

result = agent.run("Calculate 123 * 456")
```

### Multi-Agent

#### Crew

Multi-agent collaboration system.

**Usage**:
```python
from rag_chatbot.crew import Crew, CrewAgent, Task, ProcessType

# Define agents
researcher = CrewAgent(
    llm=llm,
    role="Researcher",
    goal="Find information",
    backstory="Expert researcher",
    tools=[rag_tool]
)

# Define tasks
task = Task(
    description="Research Python",
    expected_output="Python overview",
    agent=researcher
)

# Create crew
crew = Crew(
    agents=[researcher],
    tasks=[task],
    process=ProcessType.SEQUENTIAL
)

# Execute
result = crew.kickoff()
```

---

← [Architecture](Architecture.md) | [Testing](Testing.md) →
