"""Structured logging configuration for the Travel Companion Platform."""

import logging
import sys

from config import ENVIRONMENT


def setup_logging() -> logging.Logger:
    """Configure and return the application logger."""
    log_level = logging.DEBUG if ENVIRONMENT == "development" else logging.INFO
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    logger = logging.getLogger("travelcompanion")
    logger.setLevel(log_level)
    logger.addHandler(handler)
    logger.propagate = False

    return logger


logger = setup_logging()
