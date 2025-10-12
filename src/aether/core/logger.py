"""Structured logging configuration for Aether Framework.

This module provides a centralized logging setup using structlog for consistent,
machine-readable logs across the framework.

Features:
- JSON output for production (machine-readable)
- Console output for development (human-readable)
- Contextual logging (pipeline, job, dataset information)
- Automatic timestamps and log levels
- Performance tracking (duration, metrics)

Example:
    Basic logging:
    ```python
    from aether.core.logger import get_logger
    
    logger = get_logger()
    logger.info("pipeline_started", pipeline="my_pipeline", jobs=5)
    logger.error("job_failed", job="transform", error="division by zero")
    ```
    
    With context:
    ```python
    from aether.core.logger import log_context
    
    with log_context(pipeline="my_pipeline", job="transform"):
        logger.info("processing_started")  # Auto includes context
        # ... do work ...
        logger.info("processing_completed", records=1000)
    ```
"""

import logging
import sys
from contextlib import contextmanager
from typing import Any, Dict, Iterator, Optional

import structlog
from structlog.typing import EventDict, Processor


# Global flag to track if logging is configured
_LOGGING_CONFIGURED = False


def configure_logging(
    log_level: str = "INFO",
    json_output: bool = False,
    include_timestamp: bool = True,
) -> None:
    """Configure structured logging for the entire application.
    
    This should be called once at application startup (e.g., in CLI main).
    
    Args:
        log_level: Minimum log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        json_output: If True, output JSON for machine parsing.
                     If False, output human-readable console format.
        include_timestamp: Whether to include timestamps in logs.
    """
    global _LOGGING_CONFIGURED
    
    if _LOGGING_CONFIGURED:
        return  # Already configured
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stderr,  # Use stderr to avoid interfering with stdout (e.g., JSON output)
        level=getattr(logging, log_level.upper()),
    )
    
    # Build processor chain
    processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,  # Merge context vars
        structlog.stdlib.add_log_level,  # Add log level
        structlog.stdlib.add_logger_name,  # Add logger name
        structlog.processors.TimeStamper(fmt="iso", utc=True) if include_timestamp else lambda _, __, event_dict: event_dict,
        structlog.processors.StackInfoRenderer(),  # Stack traces
        structlog.processors.format_exc_info,  # Exception formatting
    ]
    
    # Add appropriate renderer
    if json_output:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(
            structlog.dev.ConsoleRenderer(
                colors=True,
                exception_formatter=structlog.dev.plain_traceback,
            )
        )
    
    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, log_level.upper())
        ),
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    _LOGGING_CONFIGURED = True


def get_logger(name: Optional[str] = None) -> Any:
    """Get a structured logger instance.
    
    Args:
        name: Logger name (usually __name__). If None, uses "aether".
    
    Returns:
        Configured structured logger (BoundLoggerLazyProxy).
    
    Example:
        ```python
        logger = get_logger(__name__)
        logger.info("event_occurred", key="value", count=42)
        ```
    """
    if not _LOGGING_CONFIGURED:
        configure_logging()  # Auto-configure with defaults
    
    logger_name = name or "aether"
    return structlog.get_logger(logger_name)


@contextmanager
def log_context(**context_vars: Any) -> Iterator[None]:
    """Context manager to bind context variables to all logs within scope.
    
    All log statements within this context will automatically include
    the provided context variables.
    
    Args:
        **context_vars: Key-value pairs to add to logging context.
    
    Yields:
        None
    
    Example:
        ```python
        with log_context(pipeline="rag_pipeline", job="embedding"):
            logger.info("started")  # Includes pipeline and job
            # ... do work ...
            logger.info("completed", records=100)  # Also includes context
        ```
        
        Nested contexts:
        ```python
        with log_context(pipeline="my_pipeline"):
            logger.info("pipeline_started")
            
            with log_context(job="transform"):
                logger.info("job_started")  # Has both pipeline and job
        ```
    """
    # Bind context to structlog's context vars (preserves existing context)
    structlog.contextvars.bind_contextvars(**context_vars)
    
    try:
        yield
    finally:
        # Unbind only the variables we added
        structlog.contextvars.unbind_contextvars(*context_vars.keys())


def reset_logging_config() -> None:
    """Reset logging configuration (mainly for testing).
    
    This allows tests to reconfigure logging with different settings.
    """
    global _LOGGING_CONFIGURED
    _LOGGING_CONFIGURED = False
    structlog.reset_defaults()


class LogCapture:
    """Utility for capturing logs in tests.
    
    Example:
        ```python
        from aether.core.logger import LogCapture, get_logger
        
        logger = get_logger()
        
        with LogCapture() as cap:
            logger.info("test_event", value=42)
            logger.error("test_error", code=500)
        
        assert len(cap.entries) == 2
        assert cap.entries[0]["event"] == "test_event"
        assert cap.entries[0]["value"] == 42
        ```
    """
    
    def __init__(self):
        """Initialize log capture."""
        self.entries: list[EventDict] = []
        self._original_processors: Optional[list[Processor]] = None
    
    def __enter__(self) -> "LogCapture":
        """Start capturing logs."""
        # Store original configuration
        config = structlog.get_config()
        self._original_processors = config.get("processors", [])
        
        # Custom processor that captures events and drops them (prevents actual logging)
        def capture_processor(
            logger: Any, method_name: str, event_dict: EventDict
        ) -> None:
            self.entries.append(event_dict.copy())
            # Raise DropEvent to prevent actual logging output
            raise structlog.DropEvent
        
        # Reconfigure with capture processor
        # Include timestamp processor before capture to ensure timestamps are in captured events
        processors = [
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),  # Add timestamps
            capture_processor,
        ]
        
        structlog.configure(
            processors=processors,
            wrapper_class=structlog.stdlib.BoundLogger,
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=False,
        )
        
        return self
    
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Stop capturing logs and restore original config."""
        # Restore original configuration
        if self._original_processors:
            structlog.configure(
                processors=self._original_processors,
                wrapper_class=structlog.stdlib.BoundLogger,
                context_class=dict,
                logger_factory=structlog.stdlib.LoggerFactory(),
                cache_logger_on_first_use=True,
            )
    
    def has_event(self, event: str) -> bool:
        """Check if a specific event was logged.
        
        Args:
            event: Event name to search for.
        
        Returns:
            True if event was found in logs.
        """
        return any(entry.get("event") == event for entry in self.entries)
    
    def get_events(self, event: str) -> list[EventDict]:
        """Get all log entries matching an event name.
        
        Args:
            event: Event name to filter by.
        
        Returns:
            List of matching log entries.
        """
        return [entry for entry in self.entries if entry.get("event") == event]
    
    def filter_by_level(self, level: str) -> list[EventDict]:
        """Get all log entries at a specific level.
        
        Args:
            level: Log level (info, warning, error, etc.).
        
        Returns:
            List of matching log entries.
        """
        return [entry for entry in self.entries if entry.get("level") == level]
