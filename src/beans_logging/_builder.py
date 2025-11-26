import os
from typing import Any

from pydantic import validate_call

from ._constants import LogHandlerTypeEnum, LogLevelEnum
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

    _handler_dict = handler.model_dump(by_alias=True, exclude_none=True)

    if _handler_dict.get("sink") is None:
        if _handler_dict.get("type") == LogHandlerTypeEnum.STD:
            _handler_dict["sink"] = std_sink
        elif _handler_dict.get("type") == LogHandlerTypeEnum.FILE:
            _logs_path: str = ""
            if _handler_dict.get("serialize") or _handler_dict.get("custom_serialize"):
                if _handler_dict.get("error"):
                    _logs_path = os.path.join(
                        config.default.file.logs_dir,
                        config.default.file.json_.err_path,
                    )
                else:
                    _logs_path = os.path.join(
                        config.default.file.logs_dir,
                        config.default.file.json_.log_path,
                    )
            else:
                if _handler_dict.get("error"):
                    _logs_path = os.path.join(
                        config.default.file.logs_dir,
                        config.default.file.plain.err_path,
                    )
                else:
                    _logs_path = os.path.join(
                        config.default.file.logs_dir,
                        config.default.file.plain.log_path,
                    )

            if "{app_name}" in _logs_path:
                _logs_path = _logs_path.format(app_name=config.app_name)

            _handler_dict["sink"] = _logs_path
    else:
        raise ValueError(
            "'sink' attribute is empty, required for any log handler except std and file handlers!"
        )

    if _handler_dict.get("level") is None:
        if _handler_dict.get("error"):
            _handler_dict["level"] = config.default.level.err
        else:
            _handler_dict["level"] = config.default.level.base

    if (_handler_dict.get("custom_serialize") is None) and _handler_dict.get(
        "serialize"
    ):
        _handler_dict["custom_serialize"] = config.default.custom_serialize

    if _handler_dict.get("custom_serialize"):
        _handler_dict["serialize"] = False
        _handler_dict["format"] = json_formatter

    if (_handler_dict.get("format") is None) and (not _handler_dict.get("serialize")):
        if _handler_dict.get("type") == LogHandlerTypeEnum.STD:
            _handler_dict["format"] = config.default.std.format_str
        else:
            _handler_dict["format"] = config.default.format_str

    if _handler_dict.get("filter") is None:
        if _handler_dict.get("type") == LogHandlerTypeEnum.STD:
            _handler_dict["filter"] = use_std_filter
        elif _handler_dict.get("type") == LogHandlerTypeEnum.FILE:
            if _handler_dict.get("serialize") or _handler_dict.get("custom_serialize"):
                if _handler_dict.get("error"):
                    _handler_dict["filter"] = use_file_json_err_filter
                else:
                    _handler_dict["filter"] = use_file_json_filter
            else:
                if _handler_dict.get("error"):
                    _handler_dict["filter"] = use_file_err_filter
                else:
                    _handler_dict["filter"] = use_file_filter
        else:
            _handler_dict["filter"] = use_all_filter

    if _handler_dict.get("backtrace") is None:
        _handler_dict["backtrace"] = True

    if (_handler_dict.get("diagnose") is None) and (
        (_handler_dict.get("level") == LogLevelEnum.TRACE)
        or (_handler_dict.get("level") == 5)
    ):
        _handler_dict["diagnose"] = True

    if (_handler_dict.get("colorize") is None) and (
        _handler_dict.get("type") == LogHandlerTypeEnum.STD
    ):
        _handler_dict["colorize"] = config.default.std.colorize

    if _handler_dict.get("type") == LogHandlerTypeEnum.FILE:
        if _handler_dict.get("enqueue") is None:
            _handler_dict["enqueue"] = True

        if _handler_dict.get("rotation") is None:
            _handler_dict["rotation"] = Rotator(
                rotate_size=config.default.file.rotate_size,
                rotate_time=config.default.file.rotate_time,
            ).should_rotate

        if _handler_dict.get("retention") is None:
            _handler_dict["retention"] = config.default.file.retention

        if _handler_dict.get("encoding") is None:
            _handler_dict["encoding"] = config.default.file.encoding

    _handler_dict.pop("type", None)
    _handler_dict.pop("error", None)
    _handler_dict.pop("custom_serialize", None)
    _handler_dict.pop("enabled", None)

    return _handler_dict


__all__ = [
    "build_handler",
]
