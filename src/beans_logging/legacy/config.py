import os
import datetime
from typing import Any
from typing_extensions import Self

from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict

from ._constants import LogLevelEnum
from ._utils import get_slug_name


class ExtraBaseModel(BaseModel):
    model_config = ConfigDict(extra="allow")


class StdHandlerConfigPM(ExtraBaseModel):
    enabled: bool = Field(default=True)


class StreamConfigPM(ExtraBaseModel):
    use_color: bool = Field(default=True)
    use_icon: bool = Field(default=False)
    format_str: str = Field(
        default=(
            "[<c>{time:YYYY-MM-DD HH:mm:ss.SSS Z}</c> | <level>{level_short:<5}</level> | <w>{name}:{line}</w>]: "
            "<level>{message}</level>"
        ),
        min_length=8,
        max_length=512,
    )
    std_handler: StdHandlerConfigPM = Field(default_factory=StdHandlerConfigPM)


class LogHandlersConfigPM(ExtraBaseModel):
    enabled: bool = Field(default=False)
    format_str: str = Field(
        default="[{time:YYYY-MM-DD HH:mm:ss.SSS Z} | {level_short:<5} | {name}:{line}]: {message}",
        min_length=8,
        max_length=512,
    )
    log_path: str = Field(
        default="{app_name}.std.all.log", min_length=4, max_length=1024
    )
    err_path: str = Field(
        default="{app_name}.std.err.log", min_length=4, max_length=1024
    )

    @model_validator(mode="after")
    def _check_log_path(self) -> Self:
        if self.log_path == self.err_path:
            raise ValueError(
                f"`log_path` and `err_path` attributes have same value: '{self.log_path}', must be different!"
            )

        return self


class JsonHandlersConfigPM(ExtraBaseModel):
    enabled: bool = Field(default=False)
    use_custom: bool = Field(default=False)
    log_path: str = Field(
        default="{app_name}.json.all.log", min_length=4, max_length=1024
    )
    err_path: str = Field(
        default="{app_name}.json.err.log", min_length=4, max_length=1024
    )

    @model_validator(mode="after")
    def _check_log_path(self) -> Self:
        if self.log_path == self.err_path:
            raise ValueError(
                f"`log_path` and `err_path` attributes have same value: '{self.log_path}', must be different!"
            )

        return self


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
    backup_count: int = Field(default=90, ge=1)
    encoding: str = Field(default="utf8", min_length=2, max_length=31)
    log_handlers: LogHandlersConfigPM = Field(default_factory=LogHandlersConfigPM)
    json_handlers: JsonHandlersConfigPM = Field(default_factory=JsonHandlersConfigPM)

    @field_validator("rotate_time", mode="before")
    @classmethod
    def _check_rotate_time(cls, val: Any) -> Any:
        if isinstance(val, str):
            val = datetime.time.fromisoformat(val)

        return val


class AutoLoadConfigPM(ExtraBaseModel):
    enabled: bool = Field(default=True)
    only_base: bool = Field(default=False)
    ignore_modules: list[str] = Field(default=[])


class InterceptConfigPM(ExtraBaseModel):
    auto_load: AutoLoadConfigPM = Field(default_factory=AutoLoadConfigPM)
    include_modules: list[str] = Field(default=[])
    mute_modules: list[str] = Field(default=[])


class ExtraConfigPM(ExtraBaseModel):
    pass


class LoggerConfigPM(ExtraBaseModel):
    app_name: str = Field(default_factory=get_slug_name, min_length=1, max_length=128)
    level: LogLevelEnum = Field(default=LogLevelEnum.INFO)
    use_backtrace: bool = Field(default=True)
    use_diagnose: bool = Field(default=False)
    stream: StreamConfigPM = Field(default_factory=StreamConfigPM)
    file: FileConfigPM = Field(default_factory=FileConfigPM)
    intercept: InterceptConfigPM = Field(default_factory=InterceptConfigPM)
    extra: ExtraConfigPM | None = Field(default_factory=ExtraConfigPM)


__all__ = [
    "StdHandlerConfigPM",
    "StreamConfigPM",
    "LogHandlersConfigPM",
    "JsonHandlersConfigPM",
    "FileConfigPM",
    "AutoLoadConfigPM",
    "InterceptConfigPM",
    "LoggerConfigPM",
]
