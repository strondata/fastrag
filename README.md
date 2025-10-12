# Aether Framework 🚀

[![Build Status](https://github.com/strondata/fastrag/workflows/PR%20Checks/badge.svg)](https://github.com/strondata/fastrag/actions)
[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> **Self-service data engineering framework with asset-centric orchestration**

Aether is a modern Python framework that orchestrates data pipelines using declarative YAML configuration, automatic dependency resolution, and built-in quality validation. Built on SOLID principles with a focus on developer experience.

---

## ✨ Key Features

- **🎯 Asset-Centric Orchestration**: Define pipelines as data assets, not just tasks
- **📋 Declarative Configuration**: YAML-based catalog and pipeline definitions
- **🔗 Automatic DAG Resolution**: Built-in dependency graph validation
- **✅ Quality-First**: Integrated Pandera and Great Expectations validators
- **🔌 Plugin Architecture**: Extensible via Protocols (no inheritance required)
- **🛠️ Rich CLI**: Interactive commands for run, visualize, test, and more
- **📊 Structured Logging**: Production-ready observability with JSON/console output
- **📈 Data-as-a-Product**: Metadata-driven approach with lineage tracking (roadmap)

---

## 🚀 Quick Start (5 minutes)

### Installation

```bash
# Using pip
pip install aether-framework

# With quality validation support
pip install aether-framework[quality]

# With RAG capabilities
pip install aether-framework[rag]

# Development setup with uv (recommended)
git clone https://github.com/strondata/fastrag.git
cd fastrag
uv venv
.\.venv\Scripts\Activate.ps1  # Windows PowerShell
uv pip install -e ".[dev,quality]"
```

### Your First Pipeline

Create a project structure:

```bash
aether new my_pipeline
cd my_pipeline
```

Define datasets in `catalog.yml`:

```yaml
raw_data:
  type: InMemoryDataSet
  layer: raw

processed_data:
  type: InMemoryDataSet
  layer: processed
  quality:
    type: PanderaValidator
    options:
      schema: "schemas.processed_schema"
```

Define your pipeline in `pipeline.yml`:

```yaml
jobs:
  transform_job:
    type: "jobs.transform.TransformJob"
    inputs:
      source: raw_data
    outputs:
      - processed_data
```

Run your pipeline:

```bash
aether run .
```

Visualize the DAG:

```bash
aether viz .
```

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                   Configuration Layer                    │
│  catalog.yml (DataSets) + pipeline.yml (Jobs/DAG)       │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                    Factory Pattern                       │
│  DataSetFactory + QualityValidatorFactory (lazy load)   │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  Asset Orchestrator                      │
│  • Build NetworkX DAG from configs                      │
│  • Validate acyclic graph                               │
│  • Execute jobs in topological order                    │
│  • Auto-inject quality validation                       │
│  • Cache dataset instances                              │
└─────────────────────────────────────────────────────────┘
```

**Core Components:**

- **Interfaces** (`core/interfaces.py`): Hybrid ABC/Protocol design
  - `IDataSet` Protocol: Extensible data connectors
  - `AbstractJob`: Template Method pattern for jobs
  - `IQualityValidator` Protocol: Pluggable validation
  
- **Configuration** (`core/config_loader.py` + `core/models.py`): Pydantic-validated YAML configs

- **Orchestrator** (`core/orchestrator.py`): DAG-based execution engine

---

## 📚 Core Concepts

### Datasets (Asset-Centric)

Datasets are the **atoms** of your pipeline. Each has a `layer` (raw, staging, processed, curated):

```yaml
employees:
  type: ParquetDataSet  # Auto-discovered by convention
  layer: curated
  options:
    path: "data/employees.parquet"
  quality:
    type: PanderaValidator
    options:
      schema: "schemas.employee_schema"
```

### Jobs (Transformations)

Jobs implement `AbstractJob` and override `_execute()`:

```python
from aether.core.interfaces import AbstractJob
from typing import Any, Dict

class UpperCaseJob(AbstractJob):
    def _execute(self, **loaded_inputs: Any) -> Dict[str, Any]:
        data = loaded_inputs["input_name"]
        result = data.upper()
        return {"output_name": result}
```

### Quality Validation

Define schemas and attach to datasets:

```python
import pandera as pa

employee_schema = pa.DataFrameSchema({
    "id": pa.Column(int, unique=True, nullable=False),
    "name": pa.Column(str, nullable=False),
    "salary": pa.Column(float, pa.Check.ge(0)),
})
```

Reference in `catalog.yml` → automatic validation before save.

---

## 🎯 Use Cases

### ✅ Data Engineering
- ETL/ELT pipelines with quality gates
- Data lake → data warehouse transformations
- Multi-source data integration

### ✅ Machine Learning
- Feature engineering pipelines
- Model training orchestration
- Experiment reproducibility

### ✅ RAG (Retrieval-Augmented Generation)
- Document embedding pipelines
- Vector index creation (Faiss)
- Knowledge base updates

### ✅ Analytics
- Business metric computation
- Report generation
- Data product delivery

---

## � Logging & Observability

Aether provides **structured logging** with full pipeline observability out of the box.

### Basic Usage

Logs are automatically emitted to **stderr** (keeping stdout clean for data) at `INFO` level:

```bash
aether run my_pipeline/
# 2025-10-12 10:30:45 [info     ] pipeline_execution_started     total_jobs=3
# 2025-10-12 10:30:45 [info     ] job_started                    job=transform_data
# 2025-10-12 10:30:46 [info     ] job_completed                  duration_seconds=0.85 job=transform_data
```

### Configuration

Control logging via environment variables:

```bash
# Change log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
export AETHER_LOG_LEVEL=DEBUG
aether run my_pipeline/

# Enable JSON output (for log aggregation systems)
export AETHER_LOG_JSON=true
aether run my_pipeline/
```

**JSON Output Example:**

```json
{
  "event": "job_completed",
  "job": "transform_data",
  "duration_seconds": 0.85,
  "records_processed": 1000,
  "timestamp": "2025-10-12T10:30:46.123Z",
  "level": "info"
}
```

### Custom Job Logging

Use `log_context()` in your jobs for automatic context binding:

```python
from aether.core.interfaces import AbstractJob
from aether.core.logger import get_logger, log_context

logger = get_logger(__name__)

class MyJob(AbstractJob):
    def _execute(self, **loaded_inputs):
        with log_context(job_param=self.params.get("key")):
            logger.info("processing_started", record_count=len(loaded_inputs["data"]))
            
            # Your logic here
            result = process(loaded_inputs["data"])
            
            logger.info("processing_completed", output_size=len(result))
            return {"output": result}
```

### Key Log Events

| Event | When | Fields |
|-------|------|--------|
| `pipeline_execution_started` | Pipeline begins | `total_jobs`, `execution_order` |
| `job_started` | Job execution starts | `job`, `num_inputs`, `num_outputs` |
| `job_completed` | Job finishes successfully | `job`, `duration_seconds` |
| `job_failed` | Job encounters error | `job`, `error`, `error_type` |
| `quality_validation_passed` | Dataset passes validation | `dataset`, `validator_type` |
| `quality_validation_failed` | Validation fails | `dataset`, `error` |
| `dataset_saved` | Dataset written to storage | `dataset`, `layer` |

### Integration with Log Aggregation

For production deployments, enable JSON logging and pipe to your log aggregation system:

```bash
# Example: Send to CloudWatch, Datadog, ELK, etc.
export AETHER_LOG_JSON=true
export AETHER_LOG_LEVEL=INFO

aether run my_pipeline/ 2>&1 | your-log-forwarder
```

---

## �🛠️ CLI Commands

| Command | Description |
|---------|-------------|
| `aether run <pipeline_dir>` | Execute pipeline with validation |
| `aether viz <pipeline_dir> [--json]` | Visualize DAG (text or JSON) |
| `aether new <project_name>` | Scaffold new project |
| `aether test <pipeline_dir>` | Validate pipeline configuration |
| `aether lint <pipeline_dir>` | Check quality schemas |
| `aether catalog <pipeline_dir>` | List datasets by layer |

---

## 📖 Documentation

- **[Getting Started Guide](design/FRAMEWORK.md)**: Deep dive into architecture
- **[Design Patterns](design/PADROES_ARQUITETURAIS.md)**: ABC vs Protocol strategy
- **[Planning Context](design/PLANNER.md)**: Jobs-to-be-Done and principles
- **[Roadmap](design/ROADMAP_COMPLETO.md)**: v0.1.0 → v1.0.0 plan
- **[Contributing](CONTRIBUTING.md)**: *(coming soon)* Development guide

---

## 🗺️ Roadmap

**Current Version:** v0.1.0-dev (~90% MVP complete)

### Milestone 1: MVP Complete (v0.1.0) - 4 weeks
- ✅ Core framework (100%)
- ✅ Quality system (Pandera + Great Expectations) (90%)
- ✅ Structured logging with structlog (100%) **← NEW!**
- ✅ Core DataSets: InMemory, Faiss, Parquet, CSV, JSON (100%)
- ✅ CLI commands: run, viz, new, test, lint, catalog (100%)
- ⚠️ DevEx: Makefile, README → **Need: CONTRIBUTING.md, issue templates**

### Milestone 2: Production-Ready (v0.2.0) - 4 weeks
- Resources system (Spark, DB connections)
- Advanced DataSets (SQL, S3, DeltaTable)
- Lineage tracking (OpenLineage)
- CI/CD auto-publish to PyPI

### Milestone 3: Developer Experience (v0.3.0) - 4 weeks
- MkDocs documentation site
- Cookiecutter project templates
- VSCode extension (DAG viz, YAML validation)

### Milestone 4: Release 1.0 (v1.0.0) - 4 weeks
- Hardening + 95%+ coverage
- Security audit
- Complete documentation
- Public launch

See **[ROADMAP_COMPLETO.md](design/ROADMAP_COMPLETO.md)** for detailed timeline.

---

## 🧪 Testing

```bash
# Run all tests
make test

# With coverage report
pytest --cov=src/aether --cov-report=html

# Specific test file
pytest tests/core/test_orchestrator.py -v

# Type checking
make type-check

# Linting
make lint
```

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) *(coming soon)* for:

- Development setup
- Code conventions
- Testing requirements
- PR process

**Quick setup:**

```bash
git clone https://github.com/strondata/fastrag.git
cd fastrag
uv venv
.\.venv\Scripts\Activate.ps1
uv pip install -e ".[dev,quality]"
make all  # lint + type-check + test
```

---

## 📊 Project Status

| Component | Status | Tests | Notes |
|-----------|--------|-------|-------|
| Core Framework | ✅ Complete | 100% | Interfaces, orchestrator, factory |
| Quality System | ✅ Complete | 100% | Pandera + Great Expectations |
| Structured Logging | ✅ Complete | 100% | structlog integration |
| DataSets | ✅ Complete | 100% | InMemory, Faiss, Parquet, CSV, JSON |
| CLI | ✅ Complete | 99% | run, viz, new, test, lint, catalog |
| DevEx Tooling | ⚠️ Partial | N/A | README ✅, CONTRIBUTING (pending) |
| Documentation | ⚠️ Partial | N/A | Design docs ✅, MkDocs (roadmap) |

**Overall Progress:** ~90% MVP → Target: 100% by end of Milestone 1

**Test Suite:** 161/162 passing (99.4%)

---

## 🌟 Philosophy

Aether follows **Data-as-a-Product** principles:

- **Data Mesh**: Domain ownership and federated governance
- **Self-Service**: Infrastructure abstraction for developers
- **Quality-First**: Built-in validation and metadata
- **Developer Experience**: Declarative configs, rich CLI, extensibility

**"The Kedro that Python deserves, with the DX that developers want!"**

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

Built with:
- [structlog](https://www.structlog.org/) for structured logging
- [Pydantic](https://pydantic.dev/) for configuration validation
- [NetworkX](https://networkx.org/) for DAG orchestration
- [Typer](https://typer.tiangolo.com/) for CLI
- [Rich](https://rich.readthedocs.io/) for beautiful terminal output
- [Pandera](https://pandera.readthedocs.io/) & [Great Expectations](https://greatexpectations.io/) for quality

---

## 📬 Contact

- **Issues**: [GitHub Issues](https://github.com/strondata/fastrag/issues)
- **Discussions**: [GitHub Discussions](https://github.com/strondata/fastrag/discussions) *(coming soon)*
- **Email**: [maintainers contact] *(to be added)*

---

**Made with ❤️ by the Aether Core Team**
