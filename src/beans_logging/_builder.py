import os
from typing import Any
from pathlib import Path

from pydantic import validate_call

from .constants import LogHandlerTypeEnum, LogLevelEnum
from .schemas import LogHandlerPM
from .config import LoggerConfigPM
from .sinks import std_sink
from .formats import json_format
from .filters import (
    all_handlers_filter,
    std_filter,
    file_filter,
    err_file_filter,
    json_filter,
    err_json_filter,
)
from .rotators import Rotator


@validate_call
def build_handler(handler: LogHandlerPM, config: LoggerConfigPM) -> dict[str, Any]:
    """Build handler config as dictionary for Loguru logger to add new handler.

    Args:
        handler (LogHandlerPM  , required): Target log handler model.
        config  (LoggerConfigPM, required): Default main config model to fill missing values.

    Raises:
        ValueError: 'sink' attribute is empty, required for any log handler except std and file handlers!

    Returns:
        dict[str, Any]: Loguru handler config as dictionary.
    """

    if handler.sink is None:
        if handler.h_type == LogHandlerTypeEnum.STD:
            handler.sink = std_sink
        else:
            raise ValueError(
                "'sink' attribute is empty, required for any log handler except std handler!"
            )

    _sink = handler.sink
    if isinstance(_sink, (str, Path)):
        if not os.path.isabs(_sink):
            _sink = os.path.join(config.file.logs_dir, _sink)

        if isinstance(_sink, Path):
            _sink = str(_sink)

        if "{app_name}" in _sink:
            _sink = _sink.format(app_name=config.app_name)

        handler.sink = _sink

    if handler.level is None:
        if handler.error:
            handler.level = config.level.err
        else:
            handler.level = config.level.base

    if (handler.use_custom_serialize is None) and handler.serialize:
        handler.use_custom_serialize = config.use_custom_serialize

    if handler.use_custom_serialize:
        handler.serialize = False
        handler.format_ = json_format

    if (handler.format_ is None) and (not handler.serialize):
        handler.format_ = config.format_str

    if handler.filter_ is None:
        if handler.h_type == LogHandlerTypeEnum.STD:
            handler.filter_ = std_filter
        elif handler.h_type == LogHandlerTypeEnum.FILE:
            if handler.serialize or handler.use_custom_serialize:
                if handler.error:
                    handler.filter_ = err_json_filter
                else:
                    handler.filter_ = json_filter
            else:
                if handler.error:
                    handler.filter_ = err_file_filter
                else:
                    handler.filter_ = file_filter
        else:
            handler.filter_ = all_handlers_filter

    if handler.backtrace is None:
        handler.backtrace = True

    if (handler.diagnose is None) and (
        (handler.level == LogLevelEnum.TRACE) or (handler.level == 5)
    ):
        handler.diagnose = True

    if handler.h_type == LogHandlerTypeEnum.FILE:
        if handler.enqueue is None:
            handler.enqueue = True

        if handler.rotation is None:
            handler.rotation = Rotator(
                rotate_size=config.file.rotate_size,
                rotate_time=config.file.rotate_time,
            ).should_rotate

        if handler.retention is None:
            handler.retention = config.file.retention

        if handler.encoding is None:
            handler.encoding = config.file.encoding

    _handler_dict = handler.model_dump(
        by_alias=True,
        exclude_none=True,
        exclude={
            "enabled",
            "h_type",
            "error",
            "use_custom_serialize",
        },
    )

    return _handler_dict


__all__ = [
    "build_handler",
]
