import os
import datetime
from typing import Any
from typing_extensions import Self

import potato_util as utils
from potato_util import io as io_utils
from pydantic import Field, model_validator, field_validator

from ._constants import LogHandlerTypeEnum, LogLevelEnum
from .schemas import ExtraBaseModel, LogHandlerPM, LoguruHandlerPM
from .sinks import std_sink
from .formats import json_format
from .filters import (
    use_all_filter,
    use_std_filter,
    use_file_filter,
    use_file_err_filter,
    use_file_json_filter,
    use_file_json_err_filter,
)
from .rotation import RotationChecker


def _get_handlers() -> list[LogHandlerPM]:

    _log_handlers: list[LogHandlerPM] = [
        LogHandlerPM(
            name="default.std_handler",
            type=LogHandlerTypeEnum.STREAM,
        ),
        LogHandlerPM(
            name="default.file_handler",
            type=LogHandlerTypeEnum.FILE,
            enabled=False,
        ),
        LogHandlerPM(
            name="default.err.file_handler",
            type=LogHandlerTypeEnum.FILE,
            is_error=True,
            enabled=False,
        ),
        LogHandlerPM(
            name="default.json.file_handler",
            type=LogHandlerTypeEnum.FILE,
            serialize=True,
            enabled=False,
        ),
        LogHandlerPM(
            name="default.json.err.file_handler",
            type=LogHandlerTypeEnum.FILE,
            serialize=True,
            is_error=True,
            enabled=False,
        ),
    ]

    return _log_handlers


class StreamConfigPM(ExtraBaseModel):
    colorize: bool = Field(default=True)
    format_str: str = Field(
        default=(
            "[<c>{time:YYYY-MM-DD HH:mm:ss.SSS Z}</c> | <level>{level_short:<5}</level> | <w>{name}:{line}</w>]: "
            "<level>{message}</level>"
        ),
        min_length=8,
        max_length=512,
    )


class PlainFileConfigPM(ExtraBaseModel):
    format_str: str = Field(
        default="[{time:YYYY-MM-DD HH:mm:ss.SSS Z} | {level_short:<5} | {name}:{line}]: {message}",
        min_length=8,
        max_length=512,
    )
    log_path: str = Field(default="{app_name}.all.log", min_length=4, max_length=1024)
    err_path: str = Field(default="{app_name}.err.log", min_length=4, max_length=1024)


class JsonFileConfigPM(ExtraBaseModel):
    log_path: str = Field(
        default="json/{app_name}.json.all.log", min_length=4, max_length=1024
    )
    err_path: str = Field(
        default="json/{app_name}.json.err.log", min_length=4, max_length=1024
    )


class FileConfigPM(ExtraBaseModel):
    logs_dir: str = Field(
        default_factory=lambda: os.path.join(os.getcwd(), "logs"),
        min_length=2,
        max_length=1024,
    )
    rotate_size: int = Field(
        default=10_000_000, ge=1_000, lt=1_000_000_000  # 10MB = 10 * 1000 * 1000
    )
    rotate_time: datetime.time = Field(default_factory=lambda: datetime.time(0, 0, 0))
    retention: int = Field(default=90, ge=1)
    encoding: str = Field(default="utf8", min_length=2, max_length=31)

    plain: PlainFileConfigPM = Field(default_factory=PlainFileConfigPM)
    json: JsonFileConfigPM = Field(default_factory=JsonFileConfigPM)


class LevelConfigPM(ExtraBaseModel):
    base: str | int | LogLevelEnum = Field(default=LogLevelEnum.INFO)
    err: str | int | LogLevelEnum = Field(default=LogLevelEnum.WARNING)

    @field_validator("base", mode="before")
    @classmethod
    def _check_level(cls, val: Any) -> Any:
        if not isinstance(val, (str, int, LogLevelEnum)):
            raise TypeError(
                f"Level attribute type {type(val).__name__} is invalid, must be str, int or <LogLevelEnum>!"
            )

        if utils.is_debug_mode() and (val != LogLevelEnum.TRACE) and (val != 5):
            val = LogLevelEnum.DEBUG

        return val


class DefaultConfigPM(ExtraBaseModel):
    level: LevelConfigPM = Field(default_factory=LevelConfigPM)
    stream: StreamConfigPM = Field(default_factory=StreamConfigPM)
    file: FileConfigPM = Field(default_factory=FileConfigPM)
    custom_json: bool = Field(default=False)


class InterceptConfigPM(ExtraBaseModel):
    enabled: bool = Field(default=True)
    only_base: bool = Field(default=False)
    ignore_modules: list[str] = Field(default=[])
    include_modules: list[str] = Field(default=[])
    mute_modules: list[str] = Field(default=[])


class ExtraConfigPM(ExtraBaseModel):
    pass


class LoggerConfigPM(ExtraBaseModel):
    app_name: str = Field(
        default_factory=utils.get_slug_name, min_length=1, max_length=128
    )
    default: DefaultConfigPM = Field(default_factory=DefaultConfigPM)
    handlers: list[LogHandlerPM] = Field(default_factory=_get_handlers)
    intercept: InterceptConfigPM = Field(default_factory=InterceptConfigPM)
    extra: ExtraConfigPM | None = Field(default_factory=ExtraConfigPM)

    @field_validator("handlers", mode="before")
    @classmethod
    def _check_handlers(cls, val: Any) -> Any:
        if val:
            if not isinstance(val, list):
                raise TypeError(
                    f"'handlers' attribute type {type(val).__name__} is invalid, must be a list of <LogHandlerPM>, <LoguruHandlerPM> or dict!"
                )

            for _i, _handler in enumerate(val):
                if not isinstance(_handler, (LogHandlerPM, LoguruHandlerPM, dict)):
                    raise TypeError(
                        f"'handlers' attribute index {_i} type {type(_handler).__name__} is invalid, must be <LogHandlerPM>, <LoguruHandlerPM> or dict!"
                    )
                elif isinstance(_handler, LoguruHandlerPM):
                    val[_i] = LogHandlerPM(
                        **_handler.model_dump(exclude_none=True, exclude_unset=True)
                    )
                elif isinstance(_handler, dict):
                    val[_i] = LogHandlerPM(**_handler)

        return val

    @model_validator(mode="after")
    def _check_all(self) -> Self:

        if "{app_name}" in self.default.file.plain.log_path:
            self.default.file.plain.log_path = self.default.file.plain.log_path.format(
                app_name=self.app_name
            )

        if "{app_name}" in self.default.file.plain.err_path:
            self.default.file.plain.err_path = self.default.file.plain.err_path.format(
                app_name=self.app_name
            )

        if "{app_name}" in self.default.file.json.log_path:
            self.default.file.json.log_path = self.default.file.json.log_path.format(
                app_name=self.app_name
            )

        if "{app_name}" in self.default.file.json.err_path:
            self.default.file.json.err_path = self.default.file.json.err_path.format(
                app_name=self.app_name
            )

        if self.handlers:
            for _handler in self.handlers:
                if _handler.sink is None:
                    if _handler.type_ == LogHandlerTypeEnum.STREAM:
                        _handler.sink = std_sink
                    elif _handler.type_ == LogHandlerTypeEnum.FILE:
                        _logs_path: str = ""
                        if _handler.serialize:
                            if _handler.is_error:
                                _logs_path = os.path.join(
                                    self.default.file.logs_dir,
                                    self.default.file.json.err_path,
                                )
                            else:
                                _logs_path = os.path.join(
                                    self.default.file.logs_dir,
                                    self.default.file.json.log_path,
                                )
                        else:
                            if _handler.is_error:
                                _logs_path = os.path.join(
                                    self.default.file.logs_dir,
                                    self.default.file.plain.err_path,
                                )
                            else:
                                _logs_path = os.path.join(
                                    self.default.file.logs_dir,
                                    self.default.file.plain.log_path,
                                )

                        _logs_dir, _ = os.path.split(_logs_path)
                        io_utils.create_dir(create_dir=_logs_dir)
                        _handler.sink = _logs_path
                    else:
                        raise ValueError(
                            "'sink' attribute is empty, required to for custom handler!"
                        )

                if _handler.level is None:
                    if _handler.is_error:
                        _handler.level = self.default.level.err
                    else:
                        _handler.level = self.default.level.base

                if _handler.filter_ is None:
                    if _handler.type_ == LogHandlerTypeEnum.STREAM:
                        _handler.filter_ = use_std_filter
                    elif _handler.type_ == LogHandlerTypeEnum.FILE:
                        if _handler.serialize:
                            if _handler.is_error:
                                _handler.filter_ = use_file_json_err_filter
                            else:
                                _handler.filter_ = use_file_json_filter
                        else:
                            if _handler.is_error:
                                _handler.filter_ = use_file_err_filter
                            else:
                                _handler.filter_ = use_file_filter
                    else:
                        _handler.filter_ = use_all_filter

                if _handler.backtrace is None:
                    _handler.backtrace = True

                if (_handler.diagnose is None) and (
                    (_handler.level == LogLevelEnum.TRACE) or (_handler.level == 5)
                ):
                    _handler.diagnose = True

                if _handler.serialize:
                    if _handler.custom_json:
                        _handler.serialize = False
                        _handler.format_ = json_format
                else:
                    if _handler.format_ is None:
                        if _handler.type_ == LogHandlerTypeEnum.STREAM:
                            _handler.format_ = self.default.stream.format_str
                        # elif _handler.type_ == LogHandlerTypeEnum.FILE:
                        else:
                            _handler.format_ = self.default.file.plain.format_str

                if ((_handler.colorize) is None) and (
                    _handler.type_ == LogHandlerTypeEnum.STREAM
                ):
                    _handler.colorize = self.default.stream.colorize

                if _handler.type_ == LogHandlerTypeEnum.FILE:
                    if _handler.enqueue is None:
                        _handler.enqueue = True

                    if _handler.rotation is None:
                        _handler.rotation = RotationChecker(
                            rotate_size=self.default.file.rotate_size,
                            rotate_time=self.default.file.rotate_time,
                        )

                    if _handler.retention is None:
                        _handler.retention = self.default.file.retention

                    if _handler.encoding is None:
                        _handler.encoding = self.default.file.encoding

        return self


__all__ = [
    "LoggerConfigPM",
]
