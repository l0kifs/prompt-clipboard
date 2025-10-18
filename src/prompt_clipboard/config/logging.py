"""
Logging configuration for the prompt-clipboard application using Loguru.

This module provides a centralized logging setup with best practices:
- Structured JSON logging for production
- Console logging with colors for development
- File logging with rotation and retention
- Proper log levels and formatting
- Error handling and context support
"""

import sys

from loguru import logger

from .settings import settings

# Remove default handler to avoid duplicate logs
logger.remove()


def setup_logging():
    """
    Configure logging for the application.

    This function sets up multiple handlers:
    - Console handler for development with colored output
    - File handler with JSON serialization for production
    - Error file handler for critical errors only
    """

    # Console handler - for development/debugging
    logger.add(
        sys.stderr,
        level=settings.logging.level,
        format=settings.logging.console_format,
        colorize=True,  # Enable colors in console
        backtrace=True,  # Show full traceback on errors
        diagnose=True,  # Show variable values in tracebacks (disable in production for security)
        enqueue=True,  # Thread-safe logging
        catch=True,  # Catch and log logging errors
    )

    # File handler - structured JSON logging
    logger.add(
        settings.log_file_path,
        level=settings.logging.file_level,
        serialize=True,  # JSON serialization
        rotation="10 MB",  # Rotate when file reaches 10MB
        retention="30 days",  # Keep logs for 30 days
        compression="gz",  # Compress rotated files
        encoding="utf-8",
        enqueue=True,
        catch=True,
    )

    # Separate error log file - only critical errors
    logger.add(
        settings.logging.dir / "errors.log",
        level="ERROR",
        serialize=True,
        rotation="1 day",  # Daily rotation for errors
        retention="90 days",  # Keep error logs longer
        compression="gz",
        encoding="utf-8",
        enqueue=True,
        catch=True,
    )

    # Add custom log level for application-specific events if needed
    # logger.level("AUDIT", no=25, color="<yellow>", icon="🔍")

    # Bind common context (can be overridden per module)
    logger.bind(app=settings.app.name, version=settings.app.version)

    # Log startup message
    logger.info(
        "Logging system initialized",
        log_file=str(settings.log_file_path),
        log_level=settings.logging.level,
    )


# Initialize logging when module is imported
setup_logging()
