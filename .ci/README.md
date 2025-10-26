# CI/CD Configuration

This directory contains the continuous integration and deployment configuration for FastRAG.

## Workflow Files

### `.ci/workflow.yml`
Reference workflow configuration that can be adapted for different CI systems (GitLab CI, Jenkins, etc.).

### `.github/workflows/test.yml`
GitHub Actions workflow that automatically runs on:
- Pushes to `main` and `develop` branches
- Pull requests targeting `main` and `develop` branches

## What the CI Pipeline Does

### 1. Test Job
Runs on multiple Python versions (3.9, 3.10, 3.11, 3.12):

- **Checkout code**: Gets the latest code
- **Setup Python**: Configures the Python environment
- **Install dependencies**: Installs all packages from `requirements.txt`
- **Lint with flake8**: Checks code quality (syntax errors, undefined names, complexity)
- **Run tests with coverage**: Executes all tests with pytest and generates coverage reports
  - XML format for Codecov
  - HTML format for human-readable reports
  - Terminal output with missing lines
- **Upload to Codecov**: Sends coverage data to Codecov (requires `CODECOV_TOKEN` secret)
- **Archive coverage reports**: Saves coverage artifacts for 30 days

### 2. Build Docker Job
Runs after tests pass:

- **Build Docker image**: Creates a Docker image from the Dockerfile
- **Test Docker image**: Runs a subset of tests inside the container

## Coverage Reports

Coverage reports are generated in multiple formats:

- **coverage.xml**: Machine-readable format for CI tools
- **htmlcov/**: HTML report with line-by-line coverage visualization
- **Terminal output**: Quick overview with missing lines

## Required Secrets

To enable Codecov integration, add this secret to your repository:

- `CODECOV_TOKEN`: Token from codecov.io for uploading coverage reports

## Running Locally

You can run the same tests locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests with coverage
pytest tests/ -v --cov=rag_chatbot --cov-report=xml --cov-report=html --cov-report=term-missing

# View HTML coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

## Customization

### Skip Slow Tests in CI

The Docker test step excludes slow tests (Embedder, VectorStore, Integration) to keep CI fast:

```bash
pytest tests/ -v -k "not Embedder and not VectorStore and not Integration"
```

### Add More Python Versions

Edit the matrix in the workflow file:

```yaml
strategy:
  matrix:
    python-version: ['3.9', '3.10', '3.11', '3.12', '3.13']
```

### Change Coverage Thresholds

Add coverage minimum to pytest config in `pytest.ini` or `pyproject.toml`:

```ini
[tool:pytest]
addopts = --cov=rag_chatbot --cov-fail-under=80
```

## CI Status Badge

Add this to your README.md to show CI status:

```markdown
![Build and Test](https://github.com/strondata/fastrag/actions/workflows/test.yml/badge.svg)
```

## Troubleshooting

### Tests timeout in CI
- Increase timeout in workflow
- Skip slow tests: `pytest -v -k "not slow"`
- Use pytest markers: `@pytest.mark.slow`

### Coverage upload fails
- Check `CODECOV_TOKEN` is set correctly
- Verify coverage.xml exists
- Set `fail_ci_if_error: false` to make it optional

### Docker build fails
- Check Dockerfile syntax
- Verify all dependencies are in requirements.txt
- Test locally: `docker build -t fastrag:test .`
