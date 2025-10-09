# FastRAG Documentation

## Overview

FastRAG is a Python library for building efficient Retrieval-Augmented Generation (RAG) systems.

## Installation

```bash
pip install -e .
```

For development:

```bash
pip install -e ".[dev]"
```

## Quick Start

```python
from fastrag import RAGSystem

# Initialize the system
rag = RAGSystem()

# Add documents
rag.add_document("Your document text here")

# Query
response = rag.query("Your question here")
print(response)
```

## API Reference

### RAGSystem

Main class for RAG functionality.

#### Methods

- `add_document(document: str)` - Add a document to the system
- `retrieve(query: str, top_k: int = 5)` - Retrieve relevant documents
- `generate(query: str, context: List[str])` - Generate a response
- `query(query: str, top_k: int = 5)` - End-to-end RAG query

### Utilities

#### chunk_text

```python
chunk_text(text: str, chunk_size: int = 512, overlap: int = 50) -> List[str]
```

Split text into chunks with optional overlap.

#### preprocess_text

```python
preprocess_text(text: str) -> str
```

Preprocess text for RAG pipeline.

## Examples

See the `examples/` directory for usage examples.

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black src/ tests/
isort src/ tests/
```

### Linting

```bash
flake8 src/ tests/
mypy src/
```
