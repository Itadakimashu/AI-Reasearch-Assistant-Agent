"""Centralized logging configuration.

Every module calls `get_logger(__name__)` instead of touching the `logging`
module directly, so log level/format stays consistent and configurable via
the `LOG_LEVEL` environment variable (see config.py).
"""
import logging
from config import settings

_CONFIGURED = False


def _configure_root() -> None:
    global _CONFIGURED
    if _CONFIGURED:
        return
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%H:%M:%S",
    )
    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    _configure_root()
    return logging.getLogger(name)
