import sys
import structlog
from config.settings import settings

def setup_logging():
    """
    Configures structured JSON logging for production readiness.
    """
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="iso"),
    ]

    if sys.stderr.isatty():
        # Pretty printing for interactive terminal
        processors.append(structlog.dev.ConsoleRenderer())
    else:
        # JSON printing for production/docker
        processors.append(structlog.processors.JSONRenderer())

    structlog.configure(
        processors=processors,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

logger = structlog.get_logger()
