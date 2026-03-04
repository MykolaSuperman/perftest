"""Structured logging for perftest application."""

import logging
import sys
from dataclasses import dataclass

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)-15s | %(message)s"


def create_logger(name: str, level: str = "INFO") -> logging.Logger:
    """Create structured logger with console handler.

    Args:
        name: Logger name
        level: Log level (DEBUG, INFO, WARNING, ERROR)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid adding multiple handlers if logger already exists
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(LOG_FORMAT))
        logger.addHandler(handler)

    return logger


@dataclass
class LogStore:
    """Centralized logger storage for different components."""

    test = create_logger("test")
    http = create_logger("http")
    metrics = create_logger("metrics")
    output = create_logger("output")
