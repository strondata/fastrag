# Quick Start Guide

Get started with FastRAG in 5 minutes!

## Prerequisites

- Python 3.9+
- Ollama installed
- 4GB+ RAM
- 5GB+ disk space

## Installation

### 1. Clone Repository

```bash
git clone https://github.com/strondata/fastrag.git
cd fastrag
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install and Configure Ollama

#### Install Ollama

**Linux/Mac:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Windows:**
Download from [ollama.com](https://ollama.com)

#### Start Ollama

```bash
ollama serve
```

#### Pull a Model

```bash
ollama pull llama3
# Or try: mistral, phi, gemma, etc.
```

## Running the Chatbot

### Using Streamlit UI

```bash
streamlit run app.py
```

Open http://localhost:8501 in your browser.

### Using Python API

```python
from rag_chatbot.core import RAGChatbot
from rag_chatbot.components.loaders import UniversalLoader
from rag_chatbot.components.embedders import MiniLMEmbedder
from rag_chatbot.components.vector_stores import ChromaVectorStore
from rag_chatbot.components.llms import OllamaLLM

# Initialize
loader = UniversalLoader()
embedder = MiniLMEmbedder()
store = ChromaVectorStore()
llm = OllamaLLM(model_name="llama3")

chatbot = RAGChatbot(loader, embedder, store, llm)

# Ingest documents
chatbot.ingest_data("./data")

# Ask questions
response = chatbot.ask("What is Python?")
print(response)
```

## Adding Documents

1. Create a `data` directory:
```bash
mkdir -p data
```

2. Add your documents (TXT, MD, PDF, DOCX):
```bash
cp my-documents/*.txt data/
```

3. In the Streamlit UI, click **"Alimentar RAG"** to ingest the documents.

## Using Docker

```bash
# Start all services
docker-compose up -d

# Pull model
docker exec -it fastrag-ollama ollama pull llama3

# Access at http://localhost:8501
```

## Configuration

Create a `.env` file:

```bash
# Copy example
cp .env.example .env

# Edit configuration
DEFAULT_LLM_MODEL=llama3
OLLAMA_HOST=http://localhost:11434
DEFAULT_EMBEDDING_MODEL=all-MiniLM-L6-v2
DATA_DIR=./data
```

## Testing

Run tests:

```bash
# All tests
pytest

# With coverage
pytest --cov=rag_chatbot

# Generate HTML report
pytest --cov=rag_chatbot --cov-report=html
```

## Next Steps

- **[Architecture](Architecture.md)** - Understand the system design
- **[Components](Components.md)** - Learn about each component
- **[Advanced Features](Advanced-Features.md)** - Explore advanced capabilities

---

← [Home](Home.md) | [Architecture](Architecture.md) →
