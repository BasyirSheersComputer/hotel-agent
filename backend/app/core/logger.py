"""
Structured Logging Configuration.
Uses structlog to output logs in JSON format for observability.
"""
import logging
import sys
import structlog
from app.config.settings import LOG_LEVEL

def configure_logging():
    """
    Configure structlog and standard logging.
    """
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
    ]

    # Decide renderer based on environment (JSON for prod, Console for dev)
    # For this SaaS readiness, we enforce JSON to meet the audit requirement.
    renderer = structlog.processors.JSONRenderer()

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            renderer,
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure standard logging to use structlog
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=LOG_LEVEL.upper() if LOG_LEVEL else logging.INFO,
    )

def get_logger(name: str):
    return structlog.get_logger(name)
