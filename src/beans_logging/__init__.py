from __future__ import annotations

from .__version__ import __version__
from .config import LoggerConfigPM
from ._core import Logger, logger, LoggerLoader


__all__ = [
    "__version__",
    "LoggerConfigPM",
    "Logger",
    "logger",
    "LoggerLoader",
]
