# flake8: noqa

import os

from . import *

logger_loader: LoggerLoader | None = None
_DISABLE_DEFAULT_LOGGER = (
    str(os.getenv("BEANS_LOGGING_DISABLE_DEFAULT")).strip().lower()
)
if (_DISABLE_DEFAULT_LOGGER != "true") and (_DISABLE_DEFAULT_LOGGER != "1"):
    logger_loader: LoggerLoader = LoggerLoader()
    logger: Logger = logger_loader.load()


__all__ = [
    "Logger",
    "logger",
    "LoggerLoader",
    "logger_loader",
    "LoggerConfigPM",
    "WarnEnum",
    "__version__",
]
