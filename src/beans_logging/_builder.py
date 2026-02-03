import os
from typing import Any
from pathlib import Path

from pydantic import validate_call

from .constants import LogHandlerTypeEnum, LogLevelEnum
from .schemas import LogHandlerPM
from .config import LoggerConfigPM
from .sinks import std_sink
from .formats import json_formatter
from .filters import (
    use_all_filter,
    use_std_filter,
    use_file_filter,
    use_file_err_filter,
    use_file_json_filter,
    use_file_json_err_filter,
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
        if handler.type_ == LogHandlerTypeEnum.STD:
            handler.sink = std_sink
        else:
            raise ValueError(
                "'sink' attribute is empty, required for any log handler except std handler!"
            )

    _sink = handler.sink
    if isinstance(_sink, (str, Path)):
        if not os.path.isabs(_sink):
            _sink = os.path.join(config.default.file.logs_dir, _sink)

        if isinstance(_sink, Path):
            _sink = str(_sink)

        if "{app_name}" in _sink:
            _sink = _sink.format(app_name=config.app_name)

        handler.sink = _sink

    if handler.level is None:
        if handler.error:
            handler.level = config.default.level.err
        else:
            handler.level = config.default.level.base

    if (handler.custom_serialize is None) and handler.serialize:
        handler.custom_serialize = config.default.custom_serialize

    if handler.custom_serialize:
        handler.serialize = False
        handler.format_ = json_formatter

    if (handler.format_ is None) and (not handler.serialize):
        handler.format_ = config.default.format_str

    if handler.filter_ is None:
        if handler.type_ == LogHandlerTypeEnum.STD:
            handler.filter_ = use_std_filter
        elif handler.type_ == LogHandlerTypeEnum.FILE:
            if handler.serialize or handler.custom_serialize:
                if handler.error:
                    handler.filter_ = use_file_json_err_filter
                else:
                    handler.filter_ = use_file_json_filter
            else:
                if handler.error:
                    handler.filter_ = use_file_err_filter
                else:
                    handler.filter_ = use_file_filter
        else:
            handler.filter_ = use_all_filter

    if handler.backtrace is None:
        handler.backtrace = True

    if (handler.diagnose is None) and (
        (handler.level == LogLevelEnum.TRACE) or (handler.level == 5)
    ):
        handler.diagnose = True

    if handler.type_ == LogHandlerTypeEnum.FILE:
        if handler.enqueue is None:
            handler.enqueue = True

        if handler.rotation is None:
            handler.rotation = Rotator(
                rotate_size=config.default.file.rotate_size,
                rotate_time=config.default.file.rotate_time,
            ).should_rotate

        if handler.retention is None:
            handler.retention = config.default.file.retention

        if handler.encoding is None:
            handler.encoding = config.default.file.encoding

    _handler_dict = handler.model_dump(
        by_alias=True,
        exclude_none=True,
        exclude={
            "enabled",
            "type_",
            "error",
            "custom_serialize",
        },
    )

    return _handler_dict


__all__ = [
    "build_handler",
]
