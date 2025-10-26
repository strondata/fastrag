# FastRAG Framework - Architecture Evolution

This document describes the complete implementation of the FastRAG framework evolution from a modular RAG pipeline to a sophisticated multi-agent system.

## Overview

The FastRAG framework has been implemented across 4 phases, each building upon the previous to create a production-ready, scalable RAG system:

1. **Phase 1**: Fundamental refactoring and core retrieval improvement
2. **Phase 2**: Intelligence and efficiency enhancement
3. **Phase 3**: Agent capabilities and memory
4. **Phase 4**: Advanced orchestration and production deployment

## Phase 1: Fundamental Refactoring

### Components Implemented

#### 1. Base Abstractions (`rag_chatbot/base.py`)

```python
from rag_chatbot.base import BaseComponent, BaseChunker, BaseRetriever, BaseReRanker, BaseGenerator
```

- **BaseComponent**: Foundation for all framework components
- **BaseChunker**: Interface for text segmentation strategies
- **BaseRetriever**: Interface for information retrieval
- **BaseReRanker**: Interface for result re-ranking
- **BaseGenerator**: Interface for LLM text generation

#### 2. Pipeline Orchestrator (`rag_chatbot/pipeline.py`)

```python
from rag_chatbot.pipeline import Pipeline

pipeline = Pipeline(
    retriever=my_retriever,
    generator=my_generator,
    reranker=my_reranker  # Optional
)

response = pipeline.run("What is RAG?")
```

Enables declarative RAG workflow construction with automatic context management.

#### 3. Semantic Chunking (`rag_chatbot/chunking.py`)

```python
from rag_chatbot.chunking import SemanticChunker

chunker = SemanticChunker(
    embedding_model=embedder,
    similarity_threshold=0.75
)

chunks = chunker.chunk(document_text)
```

Groups sentences by semantic similarity rather than arbitrary size limits, creating thematically coherent chunks.

#### 4. Hybrid Retrieval (`rag_chatbot/retrieval.py`)

```python
from rag_chatbot.retrieval import HybridRetriever, VectorRetriever, BM25Retriever

hybrid = HybridRetriever(
    vector_retriever=vector_retriever,
    bm25_retriever=bm25_retriever,
    k_rrf=60  # Reciprocal Rank Fusion constant
)

results = hybrid.retrieve(query, top_k=10)
```

Combines semantic (vector) and lexical (BM25) search using Reciprocal Rank Fusion for improved retrieval quality.

#### 5. Automated Evaluation (`.github/workflows/rag_evaluation.yml`)

GitHub Actions workflow that:
- Runs on every pull request
- Evaluates RAG performance against golden dataset
- Checks metrics (faithfulness, relevancy, precision)
- Fails builds if quality thresholds aren't met

## Phase 2: Intelligence and Efficiency

### Components Implemented

#### 1. Query Transformation (`rag_chatbot/query_transform.py`)

```python
from rag_chatbot.query_transform import QueryTransformer

transformer = QueryTransformer(llm=my_llm)

# Multi-Query: Generate variations
queries = transformer.generate_multi_queries("What is Python?", num_variations=3)

# Step-back: Create broader conceptual query
queries = transformer.generate_step_back_question("How do I use list comprehensions?")

# HyDE: Generate hypothetical answer document
hyde_doc = transformer.generate_hypothetical_document("What is machine learning?")
```

Improves retrieval by transforming queries using:
- **Multi-Query**: Generates query variations for better coverage
- **Step-back Prompting**: Creates abstract questions for principle-level retrieval
- **HyDE**: Generates hypothetical answers for semantic search

#### 2. Cross-Encoder Re-Ranking (`rag_chatbot/reranking.py`)

```python
from rag_chatbot.reranking import CrossEncoderReRanker

reranker = CrossEncoderReRanker(model_name="cross-encoder/ms-marco-MiniLM-L-6-v2")

reranked_docs = reranker.rerank(query, retrieved_docs, top_n=5)
```

Uses cross-encoder models for precise relevance scoring, applied only to top-k results for efficiency.

#### 3. Prompt Compression (`rag_chatbot/compression.py`)

```python
from rag_chatbot.compression import PromptCompressor

compressor = PromptCompressor(
    summarization_llm=fast_llm,  # Optional
    compression_ratio=0.5
)

# Heuristic compression
compressed = compressor.compress(long_prompt, method="heuristic")

# LLM-based summarization
compressed = compressor.compress(long_prompt, method="summarization")
```

Reduces token usage while preserving essential information:
- **Heuristic**: Removes redundancy and filler
- **Summarization**: Uses LLM to intelligently compress

## Phase 3: Agent Capabilities and Memory

### Components Implemented

#### 1. Tool Abstraction (`rag_chatbot/tools.py`)

```python
from rag_chatbot.tools import BaseTool, RAGTool, CalculatorTool

# Wrap RAG pipeline as a tool
rag_tool = RAGTool(rag_pipeline=my_pipeline)

# Use built-in tools
calc_tool = CalculatorTool()

# Create custom tools
class CustomTool(BaseTool):
    def use(self, input_data):
        return f"Processed: {input_data}"
```

Provides standardized interface for agent capabilities.

#### 2. ReAct Agent (`rag_chatbot/agent.py`)

```python
from rag_chatbot.agent import Agent
from rag_chatbot.tools import RAGTool, CalculatorTool

agent = Agent(
    llm=my_llm,
    tools=[rag_tool, calc_tool],
    max_iterations=5
)

response = agent.run("What is 2+2 and explain the result?", verbose=True)
```

Implements Reasoning + Acting paradigm:
1. **Thought**: Agent reasons about what to do
2. **Action**: Selects and uses a tool
3. **Observation**: Observes the result
4. **Repeat**: Continues until finding answer

#### 3. Memory Stream (`rag_chatbot/memory.py`)

```python
from rag_chatbot.memory import MemoryStream

memory = MemoryStream(
    embedder=embedder,
    vector_store=store,
    llm=llm,
    recency_weight=0.2,
    importance_weight=0.3,
    relevance_weight=0.5
)

# Add memories
memory.add_memory("User prefers concise answers", importance=8.0)

# Retrieve relevant memories
relevant_memories = memory.retrieve_memories("What format should I use?", top_k=5)
```

Sophisticated memory retrieval combining:
- **Recency**: Exponential decay over time
- **Importance**: LLM-evaluated significance (1-10)
- **Relevance**: Semantic similarity to current context

## Phase 4: Advanced Orchestration

### Components Implemented

#### 1. Multi-Agent Crews (`rag_chatbot/crew.py`)

```python
from rag_chatbot.crew import CrewAgent, Task, Crew, ProcessType

# Define specialized agents
researcher = CrewAgent(
    role="Researcher",
    goal="Find accurate information",
    backstory="Expert researcher with domain knowledge",
    tools=[rag_tool, search_tool],
    llm=my_llm
)

writer = CrewAgent(
    role="Writer",
    goal="Create engaging content",
    backstory="Professional technical writer",
    tools=[],
    llm=my_llm
)

# Define tasks
research_task = Task(
    description="Research the topic thoroughly",
    expected_output="Comprehensive research summary",
    agent=researcher
)

writing_task = Task(
    description="Write article based on research",
    expected_output="Publication-ready article",
    agent=writer
)

# Create and run crew
crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, writing_task],
    process=ProcessType.SEQUENTIAL  # or HIERARCHICAL
)

result = crew.kickoff()
```

**Sequential Process**: Tasks execute in order, each receiving previous outputs as context.

**Hierarchical Process**: Tasks can depend on specific previous tasks, enabling complex workflows.

#### 2. LLM Router (`rag_chatbot/routing.py`)

```python
from rag_chatbot.routing import Router, RoutingStrategy

router = Router(
    models={
        "simple": fast_cheap_llm,
        "complex": powerful_expensive_llm,
        "router": tiny_llm
    },
    embedder=embedder,  # For semantic routing
    default_strategy=RoutingStrategy.SEMANTIC
)

# Route query to appropriate model
selected_llm = router.route(
    "Analyze the trade-offs between X and Y",
    strategy=RoutingStrategy.LLM_JUDGE
)

response = selected_llm.generate(prompt)
```

**Routing Strategies**:
- **Semantic**: Pre-computed task category embeddings with similarity matching (fastest)
- **LLM Judge**: Uses fast LLM to classify task complexity (flexible)
- **Rule-based**: Simple heuristics on query length and keywords (no extra cost)

#### 3. Microservices Architecture (`docker-compose.production.yml`)

Production-ready architecture separating concerns:

```bash
# Start production stack
docker-compose -f docker-compose.production.yml up -d

# Scale inference service
docker-compose -f docker-compose.production.yml up -d --scale inference-service=3
```

**Services**:
- **Ingestion Service**: Batch document processing (write-only to vector DB)
- **Inference Service**: User queries and responses (read-only, horizontally scalable)
- **Streamlit UI**: Web interface
- **Qdrant**: Vector database for embeddings
- **Ollama**: Local LLM service
- **Redis**: Caching and session management
- **Nginx**: Load balancing and SSL termination

## Testing

Comprehensive test suite covering all phases:

```bash
# Run all tests
pytest

# Run specific phase tests
pytest tests/test_phase1.py  # 12 tests - Base abstractions
pytest tests/test_phase2.py  # 15 tests - Query transform, reranking
pytest tests/test_phase3.py  # 22 tests - Agents, tools, memory
pytest tests/test_phase4.py  # 15 tests - Crew, routing

# With coverage
pytest --cov=rag_chatbot --cov-report=html
```

**Total: 64 tests** covering all major components.

## Usage Examples

### Example 1: Basic RAG Pipeline

```python
from rag_chatbot.pipeline import Pipeline
from rag_chatbot.retrieval import VectorRetriever
from rag_chatbot.base import BaseGenerator

# Setup components
retriever = VectorRetriever(vector_store=store, embedder=embedder)
generator = my_llm  # Implements BaseGenerator

# Create pipeline
pipeline = Pipeline(retriever=retriever, generator=generator)

# Use pipeline
response = pipeline.run("What is machine learning?")
print(response)
```

### Example 2: Enhanced Pipeline with All Phase 2 Features

```python
from rag_chatbot.query_transform import QueryTransformer
from rag_chatbot.reranking import CrossEncoderReRanker
from rag_chatbot.compression import PromptCompressor
from rag_chatbot.retrieval import HybridRetriever

# Transform query
transformer = QueryTransformer(llm=my_llm)
queries = transformer.generate_multi_queries("What is RAG?")

# Retrieve with hybrid search
retriever = HybridRetriever(vector_retriever, bm25_retriever)
all_docs = []
for query in queries:
    all_docs.extend(retriever.retrieve(query, top_k=20))

# Re-rank
reranker = CrossEncoderReRanker()
top_docs = reranker.rerank(queries[0], all_docs, top_n=5)

# Compress prompt
context = "\n".join([doc.content for doc in top_docs])
prompt = f"Context: {context}\n\nQuestion: {queries[0]}\n\nAnswer:"

compressor = PromptCompressor(compression_ratio=0.6)
compressed_prompt = compressor.compress(prompt)

# Generate
response = my_llm.generate(compressed_prompt)
```

### Example 3: ReAct Agent with Memory

```python
from rag_chatbot.agent import Agent
from rag_chatbot.tools import RAGTool, CalculatorTool
from rag_chatbot.memory import MemoryStream

# Setup memory
memory = MemoryStream(embedder=embedder, vector_store=memory_store, llm=my_llm)

# Create agent with tools
agent = Agent(
    llm=my_llm,
    tools=[RAGTool(pipeline), CalculatorTool()],
    memory=memory
)

# Add context to memory
memory.add_memory("User prefers detailed explanations", importance=7)
memory.add_memory("Previous topic was about Python", importance=6)

# Agent uses memory and tools
response = agent.run("Calculate 15% of 200 and explain what percentage means")
```

### Example 4: Multi-Agent Research and Writing

```python
from rag_chatbot.crew import CrewAgent, Task, Crew, ProcessType

# Create specialized agents
researcher = CrewAgent(
    role="Senior Researcher",
    goal="Conduct thorough research on technical topics",
    backstory="PhD in Computer Science, 15 years industry experience",
    tools=[rag_tool, web_search_tool],
    llm=my_llm
)

analyst = CrewAgent(
    role="Data Analyst",
    goal="Analyze and synthesize research findings",
    backstory="Expert in data analysis and pattern recognition",
    tools=[calculator_tool],
    llm=my_llm
)

writer = CrewAgent(
    role="Technical Writer",
    goal="Create clear, engaging technical content",
    backstory="Award-winning technical writer",
    tools=[],
    llm=my_llm
)

# Define workflow
tasks = [
    Task(
        description="Research the current state of RAG systems",
        expected_output="Comprehensive research report with sources",
        agent=researcher
    ),
    Task(
        description="Analyze trends and patterns in the research",
        expected_output="Analysis with key insights and statistics",
        agent=analyst
    ),
    Task(
        description="Write a blog post based on research and analysis",
        expected_output="1000-word blog post in markdown format",
        agent=writer
    )
]

# Execute
crew = Crew(agents=[researcher, analyst, writer], tasks=tasks)
article = crew.kickoff()
```

## Architecture Decisions

### Why These Patterns?

1. **Component Abstraction**: Enables easy testing, swapping implementations, and extending functionality
2. **Pipeline Pattern**: Simplifies complex workflows, improves readability
3. **Hybrid Retrieval**: Combines strengths of semantic and lexical search
4. **Query Transformation**: Bridges query-document vocabulary gap
5. **Cross-Encoder Re-ranking**: Precision improvement at acceptable cost (top-k only)
6. **Prompt Compression**: Reduces latency and API costs
7. **ReAct Agent**: Natural problem-solving through reasoning and tool use
8. **Memory Stream**: Context-aware responses using past interactions
9. **Multi-Agent Crews**: Specialization improves output quality
10. **LLM Routing**: Cost optimization by matching model to task complexity
11. **Microservices**: Scalability, security, and separation of concerns

## Performance Considerations

### Optimization Tips

1. **Use semantic routing** for fastest LLM selection (no extra API call)
2. **Cache embeddings** for frequently accessed documents
3. **Apply re-ranking selectively** (top 20-50 results, return top 5)
4. **Compress prompts** for long contexts to reduce costs
5. **Batch document ingestion** to maximize throughput
6. **Scale inference service horizontally** for more users
7. **Use Redis** for caching query results and embeddings

### Cost Optimization

```python
# Example: Smart routing to minimize costs
router = Router(
    models={
        "simple": "llama2:7b",      # Free, local, fast
        "complex": "gpt-4",          # Expensive, powerful
        "router": "llama2:7b"        # Free classifier
    },
    default_strategy=RoutingStrategy.SEMANTIC  # No extra API call
)
```

## Production Deployment

### Quick Start

```bash
# 1. Clone and setup
git clone https://github.com/strondata/fastrag.git
cd fastrag

# 2. Configure environment
cp .env.example .env
# Edit .env with your settings

# 3. Start production stack
docker-compose -f docker-compose.production.yml up -d

# 4. Pull LLM models
docker exec -it fastrag-ollama ollama pull llama3

# 5. Run ingestion
docker-compose -f docker-compose.production.yml run ingestion-service python ingest.py

# 6. Access services
# - UI: http://localhost:8501
# - API: http://localhost:8000
# - Qdrant: http://localhost:6333
```

### Monitoring

```bash
# Check service health
docker-compose -f docker-compose.production.yml ps

# View logs
docker-compose -f docker-compose.production.yml logs -f inference-service

# Monitor resource usage
docker stats
```

## References

All implementations are based on established research and best practices:

1. Semantic Chunking: Content-aware segmentation
2. Hybrid Search: BM25 + Vector fusion
3. RRF: Reciprocal Rank Fusion
4. Multi-Query: Query expansion
5. Step-back Prompting: Abstract reasoning
6. HyDE: Hypothetical Document Embeddings
7. Cross-Encoders: Precise relevance scoring
8. Prompt Compression: LLMLingua and similar techniques
9. ReAct: Reasoning and Acting paradigm
10. Generative Agents: Memory with recency/importance/relevance
11. crewAI: Multi-agent collaboration
12. LLM Routing: Cost and performance optimization

## Contributing

Contributions are welcome! Please ensure:
- All tests pass: `pytest`
- Code is documented
- New features include tests
- Follows existing code style

## License

Open source - see LICENSE file for details.
