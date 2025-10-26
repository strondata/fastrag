# Advanced Features

Explore advanced RAG techniques and features.

## Hybrid Retrieval

Combine semantic (vector) and lexical (BM25) search for better results.

### Why Hybrid?

- **Semantic search**: Good for conceptual matches
- **Lexical search**: Good for exact term matches
- **Hybrid**: Best of both worlds

### Implementation

```python
from rag_chatbot.retrieval import HybridRetriever, VectorRetriever, BM25Retriever

# Create retrievers
bm25 = BM25Retriever(documents=docs)
vector = VectorRetriever(vector_store=store, embedder=embedder)

# Combine
hybrid = HybridRetriever(
    vector_retriever=vector,
    bm25_retriever=bm25,
    alpha=0.5  # Weight between methods
)

results = hybrid.retrieve("query", top_k=5)
```

### RRF (Reciprocal Rank Fusion)

Hybrid retrieval uses RRF to combine rankings:

```
score(doc) = Σ 1 / (k + rank_i(doc))
```

Where:
- `k` = 60 (constant)
- `rank_i` = rank in method i

## Reranking

Improve retrieval precision by reranking results.

### Cross-Encoder Reranking

```python
from rag_chatbot.reranking import CrossEncoderReRanker

reranker = CrossEncoderReRanker(
    model_name="cross-encoder/ms-marco-MiniLM-L-6-v2"
)

# Retrieve broadly, rerank precisely
candidates = retriever.retrieve("query", top_k=20)
reranked = reranker.rerank("query", candidates, top_k=5)
```

### Benefits

- More accurate than vector similarity alone
- Considers query-document interaction
- Trades speed for accuracy

## Query Transformation

Transform queries for better retrieval.

### Query Expansion

Expand query with related terms:

```python
from rag_chatbot.query_transform import QueryTransformer

transformer = QueryTransformer(llm=llm)

# Single expansion
expanded = transformer.expand_multi("RAG")
# ["RAG", "Retrieval Augmented Generation", "semantic search"]

# Multiple queries
queries = transformer.expand_multi("What is Python?", num_queries=3)
```

### Query Decomposition

Break complex queries into sub-queries:

```python
complex_query = "Compare Python and JavaScript for web development"
sub_queries = transformer.decompose(complex_query)
# ["What is Python used for in web development?",
#  "What is JavaScript used for in web development?",
#  "Key differences between Python and JavaScript"]
```

### Query Rewriting

Rephrase for better retrieval:

```python
vague_query = "How to make website fast?"
rewritten = transformer.rewrite_multi(vague_query)
# "What are best practices for website performance optimization?"
```

## Context Compression

Reduce context size to fit LLM limits.

### Strategies

#### 1. Heuristic Compression

```python
from rag_chatbot.compression import PromptCompressor

compressor = PromptCompressor(llm=llm)

# Compress by removing less important content
compressed = compressor.compress(
    documents,
    compression_ratio=0.5  # Keep 50%
)
```

#### 2. LLM-Based Extraction

```python
# Extract only relevant parts
compressed = compressor.compress_with_llm(
    documents,
    query="specific question"
)
```

### Benefits

- Fit more documents in context
- Reduce LLM costs
- Faster generation

## Semantic Chunking

Chunk documents based on semantic similarity instead of fixed size.

```python
from rag_chatbot.chunking import SemanticChunker

chunker = SemanticChunker(
    embedding_model=embedder,
    similarity_threshold=0.8
)

chunks = chunker.chunk(long_document)
```

### How It Works

1. Split into sentences
2. Embed each sentence
3. Group similar sentences
4. Create chunks at similarity breaks

## Multi-Agent Systems

Coordinate multiple AI agents for complex tasks.

### Use Cases

- Research + Writing
- Analysis + Synthesis
- Planning + Execution

### Example: Research Crew

```python
from rag_chatbot.crew import Crew, CrewAgent, Task, ProcessType

# Define agents
researcher = CrewAgent(
    llm=llm,
    role="Senior Researcher",
    goal="Find comprehensive information",
    backstory="PhD researcher with 10 years experience",
    tools=[rag_tool, search_tool]
)

writer = CrewAgent(
    llm=llm,
    role="Technical Writer",
    goal="Create clear documentation",
    backstory="Technical writer specializing in AI",
    tools=[]
)

# Define tasks
research_task = Task(
    description="Research RAG systems",
    expected_output="Detailed research notes",
    agent=researcher
)

writing_task = Task(
    description="Write RAG tutorial based on research",
    expected_output="Tutorial document",
    agent=writer
)

# Create and run crew
crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, writing_task],
    process=ProcessType.SEQUENTIAL
)

result = crew.kickoff()
```

## Memory Systems

Add long-term memory to agents.

### Memory Stream

Stores memories with importance and recency scoring.

```python
from rag_chatbot.memory import MemoryStream

memory = MemoryStream(
    embedder=embedder,
    vector_store=store,
    llm=llm
)

# Add memory
memory.add_memory(
    content="User prefers concise answers",
    importance=7.5
)

# Retrieve relevant memories
relevant = memory.retrieve_relevant(
    "How should I answer this?",
    k=3
)
```

### Scoring Factors

1. **Recency**: Recent memories score higher
2. **Importance**: LLM scores importance (1-10)
3. **Relevance**: Semantic similarity to query

Combined score:
```
score = α*recency + β*importance + γ*relevance
```

## Routing

Route queries to optimal models based on complexity.

```python
from rag_chatbot.routing import Router, RoutingStrategy

router = Router(
    models={
        "simple": fast_llm,    # For simple queries
        "complex": smart_llm   # For complex queries
    },
    default_strategy=RoutingStrategy.RULE_BASED
)

# Automatically route
model = router.route("Simple question")  # → fast_llm
model = router.route("Complex multi-step reasoning...")  # → smart_llm
```

### Routing Strategies

1. **Rule-Based**: Query length, keywords
2. **Semantic**: Pre-computed task embeddings
3. **LLM Judge**: Fast LLM classifies complexity

## Best Practices

### 1. Start Simple, Add Complexity

```python
# Start with basic RAG
basic_rag = RAGChatbot(loader, embedder, store, llm)

# Add features as needed
+ hybrid_retrieval
+ reranking
+ query_transformation
+ compression
```

### 2. Measure Impact

Test each feature:
- Retrieval accuracy
- Response quality
- Latency
- Cost

### 3. Optimize for Your Use Case

- **High precision needed**: Add reranking
- **Complex queries**: Use query transformation
- **Large documents**: Use semantic chunking
- **Context limits**: Add compression
- **Multi-step tasks**: Use agents

### 4. Monitor Performance

```python
import time

start = time.time()
response = chatbot.ask(query)
latency = time.time() - start

print(f"Latency: {latency:.2f}s")
print(f"Tokens: {len(response.split())}")
```

---

← [Testing](Testing.md) | [API Reference](API-Reference.md) →
