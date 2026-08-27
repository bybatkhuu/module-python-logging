# flake8: noqa

import os
from typing import Any

from potato_util import validator

_is_colorized = validator.is_truthy(
    os.environ.get("BEANS_LOGGING_AUTO_COLORIZED", "True")
)

from . import *
from .constants import DEFAULT_STD_HANDLER_NAME

_kwargs: dict[str, Any] = {"auto_load": True}
if not _is_colorized:
    _kwargs["config"] = {"handlers": {DEFAULT_STD_HANDLER_NAME: {"colorize": False}}}

logger_loader: LoggerLoader = LoggerLoader(**_kwargs)


__all__ = [
    "__version__",
    "LoggerConfigPM",
    "Logger",
    "logger",
    "LoggerLoader",
    "logger_loader",
]
