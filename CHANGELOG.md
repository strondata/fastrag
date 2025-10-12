# Changelog

All notable changes to the Aether Framework will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added - Sprint 1.5: Structured Logging (2025-10-12)

#### Core Features
- **Structured Logging Infrastructure** (`src/aether/core/logger.py`)
  - `configure_logging()`: Global configuration with JSON/console output modes
  - `get_logger()`: Factory function for configured loggers
  - `log_context()`: Context manager for automatic variable binding with proper nesting support
  - `LogCapture`: Test utility for capturing and filtering log events
  - `reset_logging_config()`: Test isolation helper

#### Integration Points
- **Orchestrator Logging** (`src/aether/core/orchestrator.py`)
  - Pipeline lifecycle events: initialization, DAG build, execution start/complete/failed
  - Job execution events: started, completed, failed (with duration tracking)
  - Quality validation events: passed, failed, skipped
  - Dataset operations: inputs loaded, outputs saved
  - Comprehensive error logging with context

- **CLI Logging** (`src/aether/cli.py`)
  - Environment-driven configuration via `AETHER_LOG_LEVEL` and `AETHER_LOG_JSON`
  - All commands emit structured logs: run, viz, test, lint, catalog
  - Clean output separation: stderr for logs, stdout for data (JSON)

#### Configuration
- **Environment Variables**
  - `AETHER_LOG_LEVEL`: Set log level (DEBUG, INFO, WARNING, ERROR, CRITICAL) - default: INFO
  - `AETHER_LOG_JSON`: Enable JSON output for log aggregation - default: false

#### Testing
- **Comprehensive Test Suite** (`tests/core/test_logger.py`)
  - 24 tests covering configuration, capture, context binding, integration, and output formats
  - Test isolation via `autouse` fixture in `conftest.py`
  - Log suppression in CLI tests (CRITICAL level) to avoid output pollution

#### Bug Fixes
- Fixed logger type annotations: Use `Any` instead of `BoundLogger` (structlog returns proxy)
- Fixed field naming: Changed `log_level` to `level` (structlog standard)
- Fixed context cleanup: Use `unbind_contextvars()` instead of `clear_contextvars()` for proper nesting
- Fixed stderr routing: Logs go to stderr, not stdout (prevents JSON output contamination)
- Fixed Rich Console: Use `print()` instead of `console.print()` for JSON commands
- Added test isolation: `autouse` fixture reconfigures logging to CRITICAL level per test

#### Documentation
- Updated README.md with comprehensive logging section
- Added logging examples: basic usage, environment configuration, custom job logging
- Documented key log events and fields
- Added integration patterns for log aggregation systems

### Added - Sprint 1.3: Core DataSets (2025-10-11)

#### DataSet Implementations
- **ParquetDataSet** (`src/aether/datasets/parquet_data_set.py`)
  - Read/write Parquet files with pandas
  - Support for partitioning, compression, and column selection
  - 21 comprehensive tests

- **CSVDataSet** (`src/aether/datasets/csv_data_set.py`)
  - Read/write CSV files with pandas
  - Configurable delimiter, encoding, header handling
  - 28 comprehensive tests

- **JSONDataSet** (`src/aether/datasets/json_data_set.py`)
  - Read/write JSON files (records or full objects)
  - Support for orient parameter (records, split, index, columns, values)
  - 31 comprehensive tests

#### Testing
- Total dataset tests: 80 (all passing)
- Coverage: edge cases, error handling, pandas integration

### Added - Sprint 1.4: Essential CLI Commands (2025-10-11)

#### CLI Commands
- **`aether test`**: Validate pipeline configuration
  - Check catalog.yml and pipeline.yml syntax
  - Validate job/dataset references
  - Verbose mode for detailed output

- **`aether lint`**: Quality schema validation
  - Check all quality validators are importable
  - Validate schema references
  - Strict mode for treating warnings as errors

- **`aether catalog`**: List datasets
  - Display datasets with type, layer, and quality info
  - Filter by layer (raw, staging, processed, curated)
  - JSON output mode for machine-readable format

#### Testing
- CLI command tests: 21 (all passing)
- Coverage: success cases, error handling, JSON output

### Added - Sprint 1.1-1.2: Foundation (2025-10-10)

#### Core Framework
- **Interfaces** (`src/aether/core/interfaces.py`)
  - `IDataSet`: Protocol for dataset implementations
  - `AbstractJob`: ABC for job implementations
  - `IQualityValidator`: Protocol for validators

- **Orchestrator** (`src/aether/core/orchestrator.py`)
  - NetworkX-based DAG execution
  - Automatic dependency resolution
  - Dataset instance caching
  - Quality validation integration

- **Factory Pattern** (`src/aether/core/factory.py`)
  - `DataSetFactory`: Convention-based lazy loading
  - `QualityValidatorFactory`: Pluggable validator discovery

- **Configuration** (`src/aether/core/config_loader.py`)
  - YAML-based catalog and pipeline definitions
  - Pydantic validation (`core/models.py`)

#### Quality System
- **Validators** (`src/aether/core/validators/`)
  - `PanderaValidator`: Schema-based DataFrame validation
  - `GreatExpectationsValidator`: Expectations-based validation

#### Initial DataSets
- `InMemoryDataSet`: Testing and prototyping
- `FaissDataSet`: Vector index storage for RAG

#### CLI Foundation
- `aether run`: Execute pipelines
- `aether viz`: Visualize DAG (text/JSON)
- `aether new`: Scaffold projects

---

## [0.1.0-dev] - 2025-10-12

### Status
- **Overall Progress**: ~90% MVP complete
- **Test Suite**: 161/162 passing (99.4%)
- **Components**:
  - Core Framework: ✅ 100%
  - Quality System: ✅ 100%
  - Structured Logging: ✅ 100%
  - DataSets: ✅ 100%
  - CLI: ✅ 100%
  - DevEx: ⚠️ Partial (README ✅, CONTRIBUTING pending)

### Known Issues
- `test_e2e_rag`: Import error for `EmbeddingJob` (pre-existing, unrelated to recent changes)

---

## Release Notes

### What's New in v0.1.0-dev

Aether Framework now includes **production-ready structured logging** with full observability:

- 📊 **Structured Logging**: JSON and console output modes with automatic context binding
- 🔍 **Full Observability**: Track pipeline execution, job performance, and quality validation
- ⚙️ **Environment Configuration**: Control via `AETHER_LOG_LEVEL` and `AETHER_LOG_JSON`
- 🧪 **Test Coverage**: 161/162 tests passing (99.4%)

Plus the complete foundation:
- ✅ Asset-centric orchestration with automatic DAG resolution
- ✅ Quality-first approach with Pandera and Great Expectations
- ✅ Rich CLI with run, viz, test, lint, catalog commands
- ✅ Core datasets: InMemory, Faiss, Parquet, CSV, JSON

Ready for Milestone 1 completion! 🚀

---

[Unreleased]: https://github.com/strondata/fastrag/compare/v0.1.0-dev...HEAD
[0.1.0-dev]: https://github.com/strondata/fastrag/releases/tag/v0.1.0-dev
