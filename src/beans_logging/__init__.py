from __future__ import annotations

from ._base import Logger, logger, LoggerLoader
from .config import LoggerConfigPM
from .__version__ import __version__


__all__ = [
    "Logger",
    "logger",
    "LoggerLoader",
    "LoggerConfigPM",
    "__version__",
]
