# Testing Guide

Comprehensive testing documentation for FastRAG.

## Test Coverage

Current coverage: **62.70%**

### Coverage by Module

| Module | Coverage | Status |
|--------|----------|--------|
| `core.py` | 100% | ✅ Excellent |
| `config.py` | 100% | ✅ Excellent |
| `components/embedders.py` | 100% | ✅ Excellent |
| `components/vector_stores.py` | 95.45% | ✅ Excellent |
| `components/loaders.py` | 90.16% | ✅ Excellent |
| `components/llms.py` | 83.33% | ✅ Good |
| `interfaces.py` | 78.79% | ✅ Good |
| `components/text_splitters.py` | 78.95% | ✅ Good |
| `tools.py` | 76.60% | ✅ Good |
| `retrieval.py` | 67.21% | ⚠️ Fair |
| `crew.py` | 60.82% | ⚠️ Fair |
| `pipeline.py` | 60.00% | ⚠️ Fair |
| `agent.py` | 58.11% | ⚠️ Fair |
| `base.py` | 54.55% | ⚠️ Fair |
| `routing.py` | 40.86% | ⚠️ Needs improvement |
| `memory.py` | 38.64% | ⚠️ Needs improvement |
| `reranking.py` | 35.29% | ⚠️ Needs improvement |
| `chunking.py` | 34.04% | ⚠️ Needs improvement |
| `query_transform.py` | 29.79% | ❌ Low |
| `compression.py` | 28.57% | ❌ Low |

## Running Tests

### All Tests

```bash
pytest
```

### With Coverage

```bash
# Terminal report
pytest --cov=rag_chatbot

# HTML report  
pytest --cov=rag_chatbot --cov-report=html
# View at htmlcov/index.html

# JSON report
pytest --cov=rag_chatbot --cov-report=json
```

### Specific Test Files

```bash
# Core tests
pytest tests/test_core.py

# Component tests
pytest tests/test_embedders.py
pytest tests/test_llms.py
pytest tests/test_vector_stores.py

# Advanced modules
pytest tests/test_all_modules.py
```

### By Markers

```bash
# Unit tests only
pytest -m unit

# Integration tests
pytest -m integration

# E2E tests
pytest -m e2e
```

### Verbose Output

```bash
pytest -v  # Verbose
pytest -vv  # Very verbose
pytest -s  # Show print statements
```

## Test Organization

### Directory Structure

```
tests/
├── __init__.py
├── test_core.py              # Core RAGChatbot tests
├── test_loaders.py           # Document loader tests
├── test_text_splitters.py    # Text splitting tests
├── test_embedders.py         # Embedding model tests
├── test_llms.py              # LLM tests
├── test_vector_stores.py     # Vector store tests
├── test_all_modules.py       # Comprehensive module tests
└── conftest.py               # Shared fixtures
```

### Test Types

#### Unit Tests
Test individual components in isolation.

```python
@pytest.mark.unit
class TestMiniLMEmbedder:
    def test_embed_documents(self, mock_sentence_transformer):
        embedder = MiniLMEmbedder()
        result = embedder.embed_documents(["text"])
        assert len(result) == 1
```

#### Integration Tests
Test component interactions.

```python
@pytest.mark.integration
class TestRAGIntegration:
    def test_full_pipeline(self, temp_dir):
        # Test loader + embedder + store together
        ...
```

#### E2E Tests
Test complete workflows.

```python
@pytest.mark.e2e
class TestRAGEndToEnd:
    def test_complete_rag_workflow(self):
        # Test ingest → query → response
        ...
```

## Writing Tests

### Basic Test Structure

```python
import pytest
from unittest.mock import Mock, patch

class TestYourComponent:
    
    @pytest.fixture
    def mock_dependency(self):
        """Create mock dependencies."""
        mock = Mock()
        mock.method.return_value = "value"
        return mock
    
    def test_feature(self, mock_dependency):
        """Test a specific feature."""
        # Arrange
        component = YourComponent(mock_dependency)
        
        # Act
        result = component.method()
        
        # Assert
        assert result == expected
```

### Using Mocks

```python
from unittest.mock import Mock, MagicMock, patch

# Mock a class
mock_llm = Mock()
mock_llm.generate.return_value = "response"

# Patch an import
@patch('rag_chatbot.components.embedders.SentenceTransformer')
def test_with_patch(mock_st):
    mock_st.return_value = MagicMock()
    # Test code
```

### Fixtures

```python
import pytest
import tempfile

@pytest.fixture
def temp_dir():
    """Temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir

@pytest.fixture
def sample_documents():
    """Sample documents for testing."""
    return [
        Documento("Content 1", {"id": "1"}),
        Documento("Content 2", {"id": "2"})
    ]
```

## Best Practices

### 1. Test Independence
Each test should be independent and not rely on others.

```python
# ✅ Good - Independent
def test_add():
    store = VectorStore()
    store.add(doc)
    assert store.count() == 1

# ❌ Bad - Depends on previous test
def test_search():
    # Assumes test_add ran first
    results = store.search(query)
```

### 2. Use Mocks Appropriately
Mock external dependencies, not the code under test.

```python
# ✅ Good - Mock external dependency
@patch('rag_chatbot.components.llms.ollama.Client')
def test_ollama_llm(mock_client):
    llm = OllamaLLM()
    llm.generate("prompt")

# ❌ Bad - Mocking the class under test
mock_llm = Mock(spec=OllamaLLM)
```

### 3. Test Edge Cases

```python
def test_empty_input():
    """Test with empty input."""
    result = function([])
    assert result == []

def test_null_input():
    """Test with None."""
    with pytest.raises(ValueError):
        function(None)

def test_large_input():
    """Test with large input."""
    large_list = ["item"] * 10000
    result = function(large_list)
    assert len(result) > 0
```

### 4. Clear Test Names

```python
# ✅ Good - Clear what is being tested
def test_embed_documents_returns_correct_dimensions():
    ...

def test_search_with_empty_query_raises_error():
    ...

# ❌ Bad - Unclear
def test_1():
    ...

def test_embedding():
    ...
```

## Coverage Goals

### Target: 90%+ Coverage

To reach 90%, focus on:

1. **Low coverage modules**:
   - `compression.py` (28.57%)
   - `query_transform.py` (29.79%)
   - `chunking.py` (34.04%)
   - `reranking.py` (35.29%)
   - `memory.py` (38.64%)

2. **Add missing test cases**:
   - Error handling paths
   - Edge cases
   - Integration scenarios

3. **Improve existing tests**:
   - Remove test stubs
   - Add assertions
   - Test actual behavior

## Continuous Integration

Tests run automatically on:
- Pull requests
- Commits to main
- Scheduled runs

### GitHub Actions

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest --cov=rag_chatbot --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## Debugging Tests

### Run specific test

```bash
pytest tests/test_core.py::TestRAGChatbot::test_ask_with_context -v
```

### Drop into debugger

```bash
pytest --pdb  # Drop into pdb on failure
pytest --pdb-trace  # Drop into pdb at start
```

### Show print statements

```bash
pytest -s
```

### Show locals on failure

```bash
pytest -l
```

---

← [Components](Components.md) | [Advanced Features](Advanced-Features.md) →
