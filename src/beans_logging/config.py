import os
import datetime
from typing import Any

import potato_util as utils
from pydantic import Field, field_validator

from .constants import LogLevelEnum, LogHandlerTypeEnum
from .schemas import ExtraBaseModel, LogHandlerPM


def get_default_handlers() -> dict[str, LogHandlerPM]:
    """Get default log handlers.

    Returns:
        dict[str, LogHandlerPM]: Default handlers as dictionary.
    """

    _log_handlers: dict[str, LogHandlerPM] = {
        "default.all.std_handler": LogHandlerPM(
            type_=LogHandlerTypeEnum.STD,
            format_=(
                "[<c>{time:YYYY-MM-DD HH:mm:ss.SSS Z}</c> | <level>{extra[level_short]:<5}</level> | "
                "<w>{name}:{line}</w>]: <level>{message}</level>"
            ),
            colorize=True,
        ),
        "default.all.file_handler": LogHandlerPM(
            enabled=False,
            type_=LogHandlerTypeEnum.FILE,
            sink="{app_name}.all.log",
        ),
        "default.err.file_handler": LogHandlerPM(
            enabled=False,
            type_=LogHandlerTypeEnum.FILE,
            sink="{app_name}.err.log",
            error=True,
        ),
        "default.all.json_handler": LogHandlerPM(
            enabled=False,
            type_=LogHandlerTypeEnum.FILE,
            sink="json/{app_name}.json.all.log",
            serialize=True,
        ),
        "default.err.json_handler": LogHandlerPM(
            enabled=False,
            type_=LogHandlerTypeEnum.FILE,
            sink="json/{app_name}.json.err.log",
            serialize=True,
            error=True,
        ),
    }

    return _log_handlers


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

    @field_validator("rotate_time", mode="before")
    @classmethod
    def _check_rotate_time(cls, val: Any) -> Any:
        if isinstance(val, str):
            val = datetime.time.fromisoformat(val)

        return val

    @field_validator("logs_dir", mode="before")
    @classmethod
    def _check_logs_dir(cls, val: Any) -> Any:
        if isinstance(val, str) and (not os.path.isabs(val)):
            val = os.path.abspath(val)

        return val


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
    format_str: str = Field(
        default="[{time:YYYY-MM-DD HH:mm:ss.SSS Z} | {extra[level_short]:<5} | {name}:{line}]: {message}",
        min_length=8,
        max_length=512,
    )
    file: FileConfigPM = Field(default_factory=FileConfigPM)
    custom_serialize: bool = Field(default=False)


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
    intercept: InterceptConfigPM = Field(default_factory=InterceptConfigPM)
    handlers: dict[str, LogHandlerPM] = Field(default_factory=get_default_handlers)
    extra: ExtraConfigPM | None = Field(default_factory=ExtraConfigPM)

    @field_validator("handlers", mode="before")
    @classmethod
    def _check_handlers(cls, val: Any) -> dict[str, LogHandlerPM]:

        if not isinstance(val, dict):
            raise TypeError(
                f"'handlers' attribute type {type(val).__name__} is invalid, must be a dict of <LogHandlerPM> or dict!"
            )

        for _key, _handler in val.items():
            if not isinstance(_handler, (LogHandlerPM, dict)):
                raise TypeError(
                    f"'handlers' attribute's '{_key}' key -> value type {type(_handler).__name__} is invalid, must be "
                    f"<LogHandlerPM> or dict!"
                )

            if isinstance(_handler, LogHandlerPM):
                val[_key] = _handler.model_dump(
                    by_alias=True, exclude_unset=True, exclude_none=True
                )

        _default_handlers = get_default_handlers()
        for _key, _handler in _default_handlers.items():
            _default_handlers[_key] = _handler.model_dump(
                by_alias=True, exclude_unset=True, exclude_none=True
            )

        if _default_handlers != val:
            val = utils.deep_merge(_default_handlers, val)

        for _key, _handler in val.items():
            val[_key] = LogHandlerPM(**_handler)

        return val


__all__ = [
    "LoggerConfigPM",
    "get_default_handlers",
]
