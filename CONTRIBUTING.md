# Contributing to Aether Framework 🤝

Thank you for your interest in contributing to Aether! This document provides guidelines and instructions for contributing to the project.

---

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Environment](#development-environment)
- [Project Structure](#project-structure)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Commit Message Convention](#commit-message-convention)

---

## 📜 Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment. We expect:

- ✅ Respectful and constructive communication
- ✅ Focus on what is best for the community
- ✅ Empathy towards other contributors
- ❌ No harassment, trolling, or discriminatory behavior

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.9+** (preferably 3.11 or 3.12)
- **uv** package manager (recommended) or pip
- **Git** for version control
- **Windows PowerShell** (for Windows) or bash (for Linux/Mac)

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:

```powershell
git clone https://github.com/YOUR_USERNAME/fastrag.git
cd fastrag
```

3. Add upstream remote:

```powershell
git remote add upstream https://github.com/strondata/fastrag.git
```

---

## 🛠️ Development Environment

### Setup with uv (Recommended)

```powershell
# Create virtual environment
uv venv

# Activate (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# Install in editable mode with dev dependencies
uv pip install -e ".[dev,quality,rag]"
```

### Setup with pip

```powershell
# Create virtual environment
python -m venv .venv

# Activate (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -e ".[dev,quality,rag]"
```

### Verify Installation

```powershell
# Run tests
make test

# Check linting
make lint

# Type checking
make type-check

# Run all checks
make all
```

---

## 📁 Project Structure

```
fastrag/
├── .github/              # GitHub Actions workflows and templates
├── design/               # Architecture and planning documents
│   ├── FRAMEWORK.md      # Core architecture
│   ├── PADROES_ARQUITETURAIS.md  # Design patterns
│   ├── PLANNER.md        # Business context
│   └── ROADMAP_COMPLETO.md  # Detailed roadmap
├── src/
│   └── aether/
│       ├── cli.py        # Typer CLI commands
│       ├── core/         # Framework internals
│       │   ├── interfaces.py     # ABCs and Protocols
│       │   ├── models.py         # Pydantic config models
│       │   ├── config_loader.py  # YAML parsing
│       │   ├── factory.py        # Factory pattern
│       │   ├── orchestrator.py   # DAG orchestrator
│       │   └── quality.py        # Quality validation
│       ├── datasets/     # IDataSet implementations
│       ├── jobs/         # AbstractJob implementations
│       └── validators/   # Quality validators
├── tests/
│   ├── conftest.py       # Pytest fixtures
│   ├── core/             # Unit tests
│   ├── pipelines/        # YAML fixtures
│   └── quality/          # Validation schemas
├── Makefile              # Development tasks
├── pyproject.toml        # Project metadata and deps
└── README.md
```

### Key Directories

- **`src/aether/core/`**: Framework internals (DO NOT import from jobs/datasets)
- **`src/aether/datasets/`**: IDataSet implementations (import core.interfaces only)
- **`src/aether/jobs/`**: AbstractJob implementations (import core.interfaces only)
- **`tests/`**: Test files mirror `src/` structure

**Import Rule**: `core` is the foundation. `datasets` and `jobs` depend only on `core.interfaces`, never each other.

---

## 🔄 Development Workflow

### 1. Create a Feature Branch

```powershell
git checkout -b feature/your-feature-name
```

Use prefixes:
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Test improvements

### 2. Make Changes

Follow [Coding Standards](#coding-standards) below.

### 3. Run Tests

```powershell
# Run all tests
make test

# Run specific test file
pytest tests/core/test_orchestrator.py -v

# With coverage
pytest --cov=src/aether --cov-report=html
```

### 4. Check Code Quality

```powershell
# Format code (auto-fix)
make format

# Lint (check only)
make lint

# Type checking
make type-check

# Run everything
make all
```

### 5. Commit Changes

Follow [Commit Message Convention](#commit-message-convention).

```powershell
git add .
git commit -m "feat: add ParquetDataSet with partitioning support"
```

### 6. Push and Open PR

```powershell
git push origin feature/your-feature-name
```

Open a Pull Request on GitHub.

---

## 🎨 Coding Standards

### Python Style

- **PEP 8** compliance (enforced by ruff)
- **Black** formatting (88 character line length)
- **Type hints** required for all public APIs
- **Docstrings** in Google style for all public functions/classes

### Type Hints Example

```python
from typing import Any, Dict, List, Optional

def load_data(path: str, columns: Optional[List[str]] = None) -> Dict[str, Any]:
    """Load data from a file.

    Args:
        path: Absolute path to the file.
        columns: Optional list of columns to load.

    Returns:
        Dictionary with loaded data.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    ...
```

### Docstring Template (Google Style)

```python
class MyClass:
    """Brief description of the class.

    Longer description with details about usage and behavior.

    Attributes:
        attr1: Description of attribute 1.
        attr2: Description of attribute 2.

    Example:
        >>> obj = MyClass(param1="value")
        >>> obj.method()
        'result'
    """

    def method(self, arg1: str, arg2: int = 0) -> str:
        """Brief description of the method.

        Args:
            arg1: Description of arg1.
            arg2: Description of arg2. Defaults to 0.

        Returns:
            Description of return value.

        Raises:
            ValueError: If arg1 is empty.
        """
        ...
```

### File Naming Conventions

- **Modules**: `snake_case.py` (e.g., `parquet_data_set.py`)
- **Classes**: `PascalCase` (e.g., `ParquetDataSet`)
- **Functions/Variables**: `snake_case` (e.g., `load_config`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `DEFAULT_BATCH_SIZE`)

---

## 🧪 Testing Guidelines

### Test Pyramid

1. **Unit Tests** (70%): Test individual components in isolation
2. **Integration Tests** (20%): Test cross-component interactions
3. **E2E Tests** (10%): Test full pipeline execution

### Writing Tests

```python
import pytest
from pathlib import Path
from aether.datasets.parquet_data_set import ParquetDataSet

def test_parquet_dataset_save_and_load(tmp_path: Path):
    """Test that ParquetDataSet can save and load data correctly."""
    # Arrange
    file_path = tmp_path / "test.parquet"
    dataset = ParquetDataSet(path=str(file_path))
    data = {"col1": [1, 2, 3], "col2": ["a", "b", "c"]}
    
    # Act
    dataset.save(data)
    loaded_data = dataset.load()
    
    # Assert
    assert loaded_data == data

def test_parquet_dataset_missing_file():
    """Test that loading non-existent file raises error."""
    dataset = ParquetDataSet(path="/nonexistent/path.parquet")
    
    with pytest.raises(FileNotFoundError):
        dataset.load()
```

### Testing Best Practices

- ✅ Use descriptive test names: `test_<what>_<condition>_<expected>`
- ✅ Follow Arrange-Act-Assert pattern
- ✅ Use `tmp_path` fixture for file I/O tests
- ✅ Mock external dependencies at boundaries only
- ✅ Test both success and failure paths
- ✅ Aim for 85%+ coverage for new code

### Running Specific Tests

```powershell
# Run tests matching pattern
pytest -k "parquet"

# Run with verbose output
pytest tests/core/test_factory.py -v

# Stop at first failure
pytest -x

# Drop to debugger on failure
pytest --pdb
```

---

## 🔀 Pull Request Process

### Before Submitting

- [ ] All tests pass (`make test`)
- [ ] Code is formatted (`make format`)
- [ ] No linting errors (`make lint`)
- [ ] Type checking passes (`make type-check`)
- [ ] Added tests for new functionality
- [ ] Updated documentation (docstrings, README if needed)
- [ ] Added entry to `CHANGELOG.md` (if applicable)

### PR Title Format

Use conventional commits prefix:

```
feat: add ParquetDataSet with partitioning support
fix: resolve DAG cycle detection bug
docs: update README with installation instructions
test: add integration tests for Great Expectations
refactor: extract factory pattern to separate module
```

### PR Description Template

```markdown
## Description
Brief summary of changes.

## Motivation and Context
Why is this change needed? What problem does it solve?

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## How Has This Been Tested?
Describe tests you ran and their results.

## Checklist
- [ ] My code follows the style guidelines of this project
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
```

### Review Process

1. **Automated Checks**: GitHub Actions will run tests, linting, and type checking
2. **Code Review**: At least one maintainer will review your PR
3. **Address Feedback**: Make requested changes
4. **Merge**: Once approved, a maintainer will merge your PR

---

## 📝 Commit Message Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style (formatting, missing semicolons, etc.)
- **refactor**: Code refactoring (no functional changes)
- **test**: Adding or updating tests
- **chore**: Maintenance tasks (deps, build, etc.)

### Examples

```bash
# Simple feature
git commit -m "feat: add CsvDataSet with encoding support"

# Bug fix with scope
git commit -m "fix(orchestrator): resolve cycle detection in DAG"

# With body
git commit -m "feat(quality): add Great Expectations validator

Implemented GreatExpectationsValidator that supports:
- Expectation suite loading from YAML
- Custom checkpoint configuration
- Detailed validation reports

Closes #42"

# Breaking change
git commit -m "feat!: change factory registration API

BREAKING CHANGE: DataSetFactory.register() now requires
explicit module path instead of auto-discovery."
```

---

## 🏗️ Adding New Components

### Adding a New DataSet

1. Create `src/aether/datasets/<snake_case_name>.py`:

```python
from typing import Any

class MyDataSet:
    """DataSet implementation for [description].
    
    Implements IDataSet protocol without inheritance.
    
    Args:
        path: Path to the data file.
        **options: Additional options.
    """
    
    def __init__(self, path: str, **options: Any):
        self.path = path
        self.options = options
    
    def load(self) -> Any:
        """Load data from the source."""
        ...
    
    def save(self, data: Any) -> None:
        """Save data to the target."""
        ...
```

2. Add tests in `tests/datasets/test_<snake_case_name>.py`

3. Use in `catalog.yml`:

```yaml
my_dataset:
  type: MyDataSet
  layer: raw
  options:
    path: "/path/to/data"
```

### Adding a New Job

1. Create job in `src/aether/jobs/<module>.py`:

```python
from typing import Any, Dict
from aether.core.interfaces import AbstractJob

class MyJob(AbstractJob):
    """Job that performs [description].
    
    Args:
        name: Job name from pipeline config.
        params: Job parameters from pipeline config.
    """
    
    def _execute(self, **loaded_inputs: Any) -> Dict[str, Any]:
        """Execute the job logic.
        
        Args:
            **loaded_inputs: Dictionary with keys matching pipeline.yml inputs.
        
        Returns:
            Dictionary with keys matching pipeline.yml outputs.
        """
        data = loaded_inputs["input_name"]
        result = transform(data)
        return {"output_name": result}
```

2. Add tests

3. Use in `pipeline.yml`:

```yaml
jobs:
  my_job:
    type: "jobs.module.MyJob"
    inputs:
      input_name: source_dataset
    outputs:
      - output_dataset
```

---

## 🐛 Reporting Bugs

Use the [Bug Report Template](.github/ISSUE_TEMPLATE/bug_report.md):

- **Clear title** describing the issue
- **Steps to reproduce** with minimal example
- **Expected vs actual behavior**
- **Environment details** (Python version, OS, etc.)
- **Error messages and stack traces**

---

## 💡 Requesting Features

Use the [Feature Request Template](.github/ISSUE_TEMPLATE/feature_request.md):

- **Problem statement**: What pain point does this solve?
- **Proposed solution**: How should it work?
- **Alternatives considered**
- **Additional context** (examples, mockups, etc.)

---

## ❓ Questions

- Check [existing issues](https://github.com/strondata/fastrag/issues)
- Use [GitHub Discussions](https://github.com/strondata/fastrag/discussions) *(coming soon)*
- Read [design docs](design/) for architecture details

---

## 📚 Additional Resources

- [README.md](README.md) - Project overview
- [design/FRAMEWORK.md](design/FRAMEWORK.md) - Architecture deep dive
- [design/PADROES_ARQUITETURAIS.md](design/PADROES_ARQUITETURAIS.md) - Design patterns
- [design/ROADMAP_COMPLETO.md](design/ROADMAP_COMPLETO.md) - Development roadmap

---

## 🙏 Thank You!

Every contribution, no matter how small, helps make Aether better. We appreciate your time and effort!

**Happy coding! 🚀**
