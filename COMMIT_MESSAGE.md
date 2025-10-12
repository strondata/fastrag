# Git Commit Message

```
feat: implement production-ready structured logging with structlog

Completes Sprint 1.5 - Logging Estruturado (Milestone 1)

## Core Features
- Structured logging infrastructure with JSON/console output modes
- Environment-driven configuration (AETHER_LOG_LEVEL, AETHER_LOG_JSON)
- Context binding with automatic nesting support
- Full observability across pipeline execution and job processing

## Implementation Details

### New Module: src/aether/core/logger.py (~282 lines)
- configure_logging(): Global setup with JSON/console rendering
- get_logger(): Factory function for configured loggers
- log_context(): Context manager for automatic variable binding
- LogCapture: Test utility for capturing log events
- reset_logging_config(): Test isolation helper

### Orchestrator Integration: src/aether/core/orchestrator.py
- Added 15+ structured log events covering:
  * Pipeline lifecycle (initialization, execution, completion, failure)
  * Job execution (started, completed, failed) with duration tracking
  * Quality validation (passed, failed, skipped)
  * Dataset operations (inputs loaded, outputs saved)
  * Comprehensive error logging with context

### CLI Integration: src/aether/cli.py
- Module-level logging configuration from environment variables
- All 5 commands emit structured logs:
  * aether run: cli_run_started/completed/failed
  * aether viz: cli_viz_started/completed
  * aether test: cli_test_started/completed
  * aether lint: cli_lint_started/completed
  * aether catalog: cli_catalog_started/completed
- Clean output separation: stderr for logs, stdout for data

### Comprehensive Testing: tests/core/test_logger.py (24 tests)
- TestLoggerConfiguration (5 tests): Setup, named loggers, log levels
- TestLogCapture (6 tests): Event capture, filtering, structured data
- TestLogContext (5 tests): Context binding, nesting, cleanup
- TestLoggingIntegration (4 tests): Pipeline patterns, error logging
- TestLoggerOutputFormats (4 tests): JSON/console rendering, timestamps

### Test Infrastructure: tests/conftest.py
- Added autouse fixture for automatic log suppression in tests
- Prevents log pollution in test output (CRITICAL level by default)
- Proper test isolation with reset_logging_config()

## Bug Fixes
1. Logger type annotations: Changed BoundLogger → Any (structlog returns proxy)
2. Field naming: Standardized on 'level' instead of 'log_level' (structlog convention)
3. Context cleanup: Use unbind_contextvars() for proper nesting support
4. Stderr routing: Logs go to stderr, not stdout (prevents JSON contamination)
5. Rich Console: Use print() instead of console.print() for JSON output
6. Test isolation: autouse fixture reconfigures logging per test

## Documentation Updates
- README.md: Added comprehensive "Logging & Observability" section with usage examples
- CHANGELOG.md: New file documenting all Sprint 1.5 changes
- PR_SUMMARY.md: Detailed summary for PR review

## Dependencies
- Added structlog>=25.0.0 to core dependencies in pyproject.toml

## Test Results
- 161/162 tests passing (99.4%)
- Only failure: test_e2e_rag (pre-existing, unrelated to logging)
- Logger tests: 24/24 ✅
- Orchestrator tests: 3/3 ✅ (with logging)
- CLI tests: 28/28 ✅ (with logging)
- All other component tests passing

## Breaking Changes
None - purely additive functionality

## Usage Examples

Basic logging (default):
```bash
$ aether run my_pipeline/
2025-10-12 10:30:45 [info] pipeline_execution_started total_jobs=3
```

JSON logging (production):
```bash
$ export AETHER_LOG_JSON=true
$ aether run my_pipeline/
{"event":"pipeline_execution_started","total_jobs":3,"timestamp":"2025-10-12T10:30:45.123Z","level":"info"}
```

Custom job logging:
```python
from aether.core.logger import get_logger, log_context

logger = get_logger(__name__)

with log_context(job_param=self.params.get("key")):
    logger.info("processing_started", record_count=100)
```

## Milestone Progress
Sprint 1.5: COMPLETE ✅ (6/6 tasks)
Milestone 1: ~90% complete (was 85% at sprint start)

Closes #<issue-number> (if applicable)
```
