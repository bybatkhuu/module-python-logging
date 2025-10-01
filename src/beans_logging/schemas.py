# -*- coding: utf-8 -*-

import datetime
from typing import List


import pydantic
from pydantic import BaseModel, constr, Field

if "2.0.0" <= pydantic.__version__:
    from pydantic import field_validator, model_validator, ConfigDict
else:
    from pydantic import validator, root_validator


from ._consts import LogLevelEnum
from ._utils import get_default_logs_dir, get_app_name


class ExtraBaseModel(BaseModel):
    if "2.0.0" <= pydantic.__version__:
        model_config = ConfigDict(extra="allow")
    else:

        class Config:
            extra = "allow"


class StdHandlerPM(ExtraBaseModel):
    enabled: bool = Field(default=True)


class StreamPM(ExtraBaseModel):
    use_color: bool = Field(default=True)
    use_icon: bool = Field(default=False)
    format_str: constr(strip_whitespace=True) = Field(
        default="[<c>{time:YYYY-MM-DD HH:mm:ss.SSS Z}</c> | <level>{level_short:<5}</level> | <w>{name}:{line}</w>]: <level>{message}</level>",
        min_length=3,
        max_length=511,
    )
    std_handler: StdHandlerPM = Field(default_factory=StdHandlerPM)


class LogHandlersPM(ExtraBaseModel):
    enabled: bool = Field(default=False)
    format_str: constr(strip_whitespace=True) = Field(
        default="[{time:YYYY-MM-DD HH:mm:ss.SSS Z} | {level_short:<5} | {name}:{line}]: {message}",
        min_length=4,
        max_length=511,
    )
    log_path: constr(strip_whitespace=True) = Field(
        default="{app_name}.std.all.log", min_length=4, max_length=1023
    )
    err_path: constr(strip_whitespace=True) = Field(
        default="{app_name}.std.err.log", min_length=4, max_length=1023
    )

    if "2.0.0" <= pydantic.__version__:

        @model_validator(mode="after")
        def _check_log_path(self) -> "LogHandlersPM":
            if self.log_path == self.err_path:
                raise ValueError(
                    f"`log_path` and `err_path` attributes are same: '{self.log_path}', must be different!"
                )
            return self

    else:

        @root_validator
        def _check_log_path(cls, values):
            _log_path, _err_path = values.get("log_path"), values.get("err_path")
            if _log_path == _err_path:
                raise ValueError(
                    f"`log_path` and `err_path` attributes are same: '{_log_path}', must be different!"
                )
            return values


class JsonHandlersPM(ExtraBaseModel):
    enabled: bool = Field(default=False)
    use_custom: bool = Field(default=False)
    log_path: constr(strip_whitespace=True) = Field(
        default="{app_name}.json.all.log", min_length=4, max_length=1023
    )
    err_path: constr(strip_whitespace=True) = Field(
        default="{app_name}.json.err.log", min_length=4, max_length=1023
    )

    if "2.0.0" <= pydantic.__version__:

        @model_validator(mode="after")
        def _check_log_path(self) -> "JsonHandlersPM":
            if self.log_path == self.err_path:
                raise ValueError(
                    f"`log_path` and `err_path` attributes are same: '{self.log_path}', must be different!"
                )
            return self

    else:

        @root_validator
        def _check_log_path(cls, values):
            _log_path, _err_path = values.get("log_path"), values.get("err_path")
            if _log_path == _err_path:
                raise ValueError(
                    f"`log_path` and `err_path` attributes are same: '{_log_path}', must be different!"
                )
            return values


class FilePM(ExtraBaseModel):
    logs_dir: constr(strip_whitespace=True) = Field(
        default_factory=get_default_logs_dir, min_length=2, max_length=1023
    )
    rotate_size: int = Field(
        default=10_000_000, ge=1_000, lt=1_000_000_000  # 10MB = 10 * 1000 * 1000
    )
    rotate_time: datetime.time = Field(datetime.time(0, 0, 0))
    backup_count: int = Field(default=90, ge=1)
    encoding: constr(strip_whitespace=True) = Field(
        default="utf8", min_length=2, max_length=31
    )
    log_handlers: LogHandlersPM = Field(default_factory=LogHandlersPM)
    json_handlers: JsonHandlersPM = Field(default_factory=JsonHandlersPM)

    if "2.0.0" <= pydantic.__version__:

        @field_validator("rotate_time", mode="before")
        @classmethod
        def _check_rotate_time(cls, val):
            if isinstance(val, str):
                val = datetime.time.fromisoformat(val)
            return val

    else:

        @validator("rotate_time", pre=True, always=True)
        def _check_rotate_time(cls, val):
            if val and isinstance(val, str):
                val = datetime.time.fromisoformat(val)
            return val


class AutoLoadPM(ExtraBaseModel):
    enabled: bool = Field(default=True)
    only_base: bool = Field(default=False)
    ignore_modules: List[str] = Field(default=[])


class InterceptPM(ExtraBaseModel):
    auto_load: AutoLoadPM = Field(default_factory=AutoLoadPM)
    include_modules: List[str] = Field(default=[])
    mute_modules: List[str] = Field(default=[])


class ExtraPM(ExtraBaseModel):
    pass


class LoggerConfigPM(ExtraBaseModel):
    app_name: constr(strip_whitespace=True) = Field(
        default_factory=get_app_name,
        min_length=1,
        max_length=127,
    )
    level: LogLevelEnum = Field(default=LogLevelEnum.INFO)
    use_backtrace: bool = Field(default=True)
    use_diagnose: bool = Field(default=False)
    stream: StreamPM = Field(default_factory=StreamPM)
    file: FilePM = Field(default_factory=FilePM)
    intercept: InterceptPM = Field(default_factory=InterceptPM)
    extra: ExtraPM = Field(default_factory=ExtraPM)
