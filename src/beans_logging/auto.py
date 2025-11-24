# flake8: noqa

from . import *

logger_loader: LoggerLoader = LoggerLoader()
logger = logger_loader.load()


__all__ = [
    "logger",
    "LoggerLoader",
    "logger_loader",
    "LoggerConfigPM",
    "__version__",
]
