# Aether Framework - AI Coding Agent Instructions

## Project Overview

**Aether** is a self-service data engineering framework that orchestrates data pipelines using a hybrid asset-centric approach. It's built in Python with a focus on SOLID principles, declarative configuration, and developer experience.

**Core Philosophy**: Data-as-a-Product (DaaP) with metadata-driven orchestration, where pipelines are declared in YAML and the framework handles dependency resolution, execution order, and quality validation.

**Business Context** (from `design/PLANNER.md`):
- **Mission**: Migrate from "service desk" model to proactive product team
- **Jobs-to-be-Done (JTBD)**: Framework addresses pain points of Data Engineers (boilerplate code, debugging), Data Scientists (data trust, reproducibility), and Business Analysts (single source of truth)
- **Principles**: Data Mesh (domain ownership), Self-Service (infrastructure abstraction), Federated Computational Governance (built-in quality)

**Project Status** (v0.1.0-dev):
- 📊 **Overall**: 65% MVP complete
- ✅ **Core Framework**: 100% (interfaces, orchestrator, config)
- ✅ **Quality System**: 90% (Pandera + Great Expectations)
- ⚠️ **DataSets**: 20% (InMemory, Faiss only)
- ⚠️ **CLI**: 60% (run, viz, new only)
- ❌ **DevEx**: 15% (Makefile only - no docs, cookiecutter, or VSCode extension)

**Execution Environment Roadmap**:
- **Current**: Local Python execution
- **Planned**: Databricks/Spark integration via Databricks Connect (see `design/FRAMEWORK.md` §7)
- **Future**: Docker, serverless (AWS Lambda/Azure Functions)

## Architecture Fundamentals

### Hybrid Typing Strategy (Critical)

Aether uses a **deliberate hybrid approach** to interfaces:

- **Protocols (`typing.Protocol`)** for plugin points: `IDataSet`, `IQualityValidator` allow external integrations without inheritance
- **Abstract Base Classes (ABC)** for core components: `AbstractJob`, `AbstractPipeline` provide shared behavior and runtime enforcement

**Why this matters**: When extending the framework:
- New data connectors → implement `IDataSet` protocol (no inheritance required)
- New jobs → inherit from `AbstractJob` (gets lifecycle management)
- New validators → implement `IQualityValidator` protocol

See `src/aether/core/interfaces.py` and `design/PADROES_ARQUITETURAIS.md` for detailed rationale.

### Key Components and Data Flow

1. **Configuration Layer** (`core/config_loader.py` + `core/models.py`):
   - `catalog.yml` → `CatalogConfig` (Pydantic) defines datasets
   - `pipeline.yml` → `PipelineConfig` (Pydantic) defines jobs and DAG
   - All configs validated at load time

2. **Factory Pattern** (`core/factory.py`):
   - `DataSetFactory`: lazy-loads dataset classes by convention (`TypeName` → `aether.datasets.type_name.TypeName`)
   - `QualityValidatorFactory`: lazy-loads validators similarly
   - Both use registry + lazy import for extensibility

3. **Orchestration** (`core/orchestrator.py`):
   - `AssetOrchestrator` builds a NetworkX DAG from configs
   - Validates DAG is acyclic at construction time
   - Executes jobs in topological order
   - Caches dataset instances to avoid recreation
   - Automatically injects quality validation between job execution and dataset save

4. **Job Execution Pattern**:
   ```python
   # Jobs implement Template Method pattern:
   def run(self, **inputs: IDataSet) -> Dict[str, Any]:
       loaded_inputs = {key: ds.load() for key, ds in inputs.items()}
       return self._execute(**loaded_inputs)  # Override this
   ```

### Layer Conventions

Datasets have a `layer` field (enforced in `catalog.yml`):
- `raw`: Source data, unchanged
- `staging`/`transient`: Intermediate transformations
- `processed`: Business logic applied
- `curated`: Final, quality-validated outputs

## Development Workflows

### Running Commands (Windows PowerShell)

**Critical**: This project uses `uv` for dependency management and Makefile for task automation:

```powershell
# Setup (first time)
uv venv
.\.venv\Scripts\Activate.ps1
uv pip install -e ".[dev]"

# Common workflows
make lint        # ruff + black (check only)
make format      # Auto-fix formatting
make type-check  # mypy
make test        # pytest with all fixtures
make all         # Run lint + type-check + test
```

### Testing Strategy

**Pyramid approach** (see `tests/`):

1. **Unit tests** (`tests/core/`): Test individual components in isolation
   - Mock external dependencies only at boundaries
   - Use `tmp_path` fixture for file I/O tests
   - Example: `test_factory.py`, `test_quality.py`

2. **Integration tests** (`tests/core/test_orchestrator.py`): 
   - Use real instances of internal components
   - Validate cross-component interactions
   - Test error paths (cycles, missing outputs, quality failures)

3. **E2E tests** (`tests/test_e2e_rag.py`):
   - Execute full pipelines via CLI
   - Verify file artifacts created
   - Use `typer.testing.CliRunner`

**Key fixture**: `test_pipeline_path` in `conftest.py` scaffolds a complete pipeline directory with `catalog.yml` + `pipeline.yml`.

### CLI Commands (via Typer)

```bash
aether run <pipeline_dir>          # Execute pipeline
aether viz <pipeline_dir> [--json] # Visualize DAG
aether new <project_name>          # Scaffold new project
```

**Implementation note**: CLI delegates to `AssetOrchestrator` after config loading. All business logic stays in core modules, not CLI.

## Code Patterns and Conventions

### Adding a New DataSet Type

1. Create `src/aether/datasets/<snake_case_name>.py`
2. Implement `IDataSet` protocol (no inheritance):
   ```python
   class MyDataSet:
       def __init__(self, **options):
           self.options = options
       
       def load(self) -> Any: ...
       def save(self, data: Any) -> None: ...
   ```
3. Use in `catalog.yml`:
   ```yaml
   my_dataset:
     type: MyDataSet  # Factory auto-discovers by convention
     layer: raw
     options:
       path: "/data/file.ext"
   ```

### Adding Quality Validation

Define schema in `tests/quality/schemas.py` (or project-specific module):
```python
import pandera as pa

employee_schema = pa.DataFrameSchema({
    "id": pa.Column(int, unique=True),
    "name": pa.Column(str, nullable=False),
})
```

Reference in `catalog.yml`:
```yaml
employees:
  type: ParquetDataSet
  layer: curated
  quality:
    type: PanderaValidator
    options:
      schema: "tests.quality.schemas.employee_schema"
```

Orchestrator auto-validates before saving. Failures raise `QualityCheckError`.

### Job Implementation Pattern

```python
from aether.core.interfaces import AbstractJob

class MyTransformJob(AbstractJob):
    def _execute(self, **loaded_inputs: Any) -> Dict[str, Any]:
        # loaded_inputs keys match pipeline.yml inputs mapping
        data = loaded_inputs["input_name"]
        
        # Apply transformation
        result = transform(data)
        
        # Return dict with keys matching pipeline.yml outputs
        return {"output_name": result}
```

**Critical**: Job constructors receive `name` and `params` from `pipeline.yml`. Call `super().__init__(name, params)` to store them.

## Common Pitfalls

1. **Naming Convention Mismatch**: Factory expects `TypeName` → `type_name.py`. Inconsistent casing breaks lazy loading.
   - ✅ Correct: `ParquetDataSet` class in `src/aether/datasets/parquet_data_set.py`
   - ❌ Wrong: `ParquetDataSet` class in `src/aether/datasets/parquet.py`

2. **Job Output Mismatch**: `_execute()` must return dict with keys matching ALL `outputs:` in `pipeline.yml`. Missing keys raise `OrchestratorError`.
   - Example from `tests/core/test_orchestrator.py`: Job declares 2 outputs but returns 1 → runtime error

3. **Circular Dependencies**: Define jobs in execution order. Orchestrator validates DAG at construction time (raises on cycles), but error messages reference dataset names, not jobs.

4. **Quality Schema Paths**: Must be importable Python paths like `module.schema_name`, not file paths.
   - ✅ Correct: `"tests.quality.schemas.employee_schema"`
   - ❌ Wrong: `"tests/quality/schemas.py:employee_schema"`

5. **Dataset Instance Caching**: Orchestrator caches by dataset name. Don't mutate `options` after factory creation.

6. **Missing Documentation**: README.md is currently just "# fastrag\nO seu consagrado" - needs complete rewrite (see Milestone 1 priorities).

7. **DevEx Tooling Absent**: No MkDocs, no Cookiecutter, no VSCode extension - only Makefile exists. Check `design/DEVEX.py` for implementation roadmap.

## Roadmap Context (v0.1.0 → v1.0.0)

**Current Status** (65% MVP - see `design/ROADMAP_COMPLETO.md`):
- ✅ Core framework complete (interfaces, orchestrator, factory pattern)
- ✅ Quality system (Pandera + Great Expectations validators)
- ⚠️ Limited dataset types (InMemory, Faiss only - no Parquet/CSV/SQL)
- ⚠️ Basic CLI (missing `test`, `lint`, `catalog`, `docs` subcommands)
- ❌ **NO DevEx tooling**: README is placeholder ("O seu consagrado"), no CONTRIBUTING.md, no MkDocs, no Cookiecutter template, no VSCode extension

**Milestone 1 - MVP Completo (v0.1.0)** - 4 weeks:
1. **Week 1-2**: Documentation (README.md, CONTRIBUTING.md, issue templates) + Core DataSets (Parquet, CSV, JSON)
2. **Week 3-4**: Complete CLI (`aether test`, `aether lint`, `aether catalog`) + Structured logging (structlog)

**Milestone 2 - Produtização (v0.2.0)** - 4 weeks:
- Resources system (`IResource` protocol for Spark, DB connections)
- Advanced DataSets (SQL, S3, DeltaTable)
- Lineage tracking (OpenLineage format)
- CI/CD publish workflow

**Milestone 3 - DevEx Avançado (v0.3.0)** - 4 weeks:
- MkDocs + Material theme + auto-deploy to GitHub Pages
- Cookiecutter template (replace basic `aether new`)
- VSCode extension (DAG visualization webview, TaskProvider, YAML schema validation)

**Architecture Decisions Reference**:
- `design/FRAMEWORK.md`: Asset-centric orchestration philosophy, Databricks integration strategy
- `design/PADROES_ARQUITETURAIS.md`: Hybrid ABC/Protocol strategy rationale
- `design/PLANNER.md`: Jobs-to-be-Done framework, Data-as-a-Product principles, persona pain points
- `design/DEVEX.py`: DevEx status analysis (15% implemented - Makefile only)

## File Organization Rules

```
src/aether/
├── core/          # Framework internals (DO NOT import from jobs/datasets)
├── datasets/      # IDataSet implementations (import core.interfaces only)
├── jobs/          # AbstractJob implementations (import core.interfaces only)
└── cli.py         # Thin wrapper over core.orchestrator

tests/
├── core/          # Unit tests mirror src/aether/core structure
├── pipelines/     # YAML fixtures for integration tests
└── quality/       # Shared validation schemas
```

**Import rule**: `core` is the foundation. `datasets` and `jobs` depend only on `core.interfaces`, never each other.

## Documentation Standards

- **Docstrings**: Use Google-style with `Args:` and `Returns:` sections
- **Type hints**: Required for all public APIs (mypy enforced in CI)
- **YAML comments**: Explain non-obvious configuration choices
- **Design docs**: Update `design/` when making architectural changes

## Testing Quick Reference

```powershell
# Run specific test file
pytest tests/core/test_orchestrator.py -v

# Run with coverage
pytest --cov=src/aether --cov-report=html

# Run only RAG tests
pytest -k rag

# Debug test failures
pytest --pdb -x  # Drop to debugger on first failure
```

**Assertion patterns**:
- Use `pytest.raises(SpecificError, match="pattern")` for error tests
- Access orchestrator internals via `orchestrator.instance_cache` in tests
- Validate file outputs with `Path.exists()` and content reads

---

**When in doubt**: Check existing implementations in `src/aether/` before creating new patterns. This framework values consistency over cleverness.
