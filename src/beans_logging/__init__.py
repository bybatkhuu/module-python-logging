from __future__ import annotations

from .__version__ import __version__
from .schemas import LoguruHandlerPM, LogHandlerPM
from .config import get_default_handlers, LoggerConfigPM
from ._core import Logger, logger, LoggerLoader


__all__ = [
    "__version__",
    "LoguruHandlerPM",
    "LogHandlerPM",
    "get_default_handlers",
    "LoggerConfigPM",
    "Logger",
    "logger",
    "LoggerLoader",
]
