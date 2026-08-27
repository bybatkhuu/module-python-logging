# flake8: noqa

import os
from typing import Any

from potato_util import validator

_is_colorized = validator.is_truthy(
    os.environ.get("BEANS_LOGGING_AUTO_COLORIZED", "True")
)
_format = os.environ.get("BEANS_LOGGING_AUTO_FORMAT")

from . import *
from .constants import DEFAULT_STD_HANDLER_NAME

_kwargs: dict[str, Any] = {"auto_load": True}
_handler_config: dict[str, Any] = {}

if not _is_colorized:
    _handler_config["colorize"] = False

if _format:
    _handler_config["format_"] = _format

if _handler_config:
    _kwargs["config"] = {"handlers": {DEFAULT_STD_HANDLER_NAME: _handler_config}}

logger_loader: LoggerLoader = LoggerLoader(**_kwargs)


__all__ = [
    "__version__",
    "LoggerConfigPM",
    "Logger",
    "logger",
    "LoggerLoader",
    "logger_loader",
]
