import logging
import datetime
from pathlib import Path
from asyncio import AbstractEventLoop
from multiprocessing.context import BaseContext
from typing import Any, IO, Union, Protocol, Dict
from collections.abc import Callable, Awaitable

from pydantic import BaseModel, Field, ConfigDict
from loguru import Record

from ._constants import HandlerTypeEnum, LogLevelEnum


class ExtraBaseModel(BaseModel):
    model_config = ConfigDict(extra="allow")


class SupportsWrite(Protocol):
    def write(self, __s: str) -> Any: ...
    def flush(self) -> Any: ...


SinkType = Union[
    str,
    Path,
    IO[str],
    SupportsWrite,
    Callable[[Any], Any],
    Callable[[Any], Awaitable[Any]],
    logging.Handler,
]

FilterType = Union[Callable[[Record], bool], str, dict[str, Any], None]

RotationType = Union[
    str, int, datetime.time, datetime.timedelta, Callable[[str, Any], bool], None
]

RetentionType = Union[str, int, datetime.timedelta, Callable[[Any], None], None]


class HandlerPM(ExtraBaseModel):
    name: str = Field(...)
    enabled: bool = Field(default=True)
    type_: HandlerTypeEnum = Field(...)
    sink: SinkType = Field(...)
    level: str | int | LogLevelEnum | None = Field(default=LogLevelEnum.INFO)
    format_: str | Callable[[Any], str] | None = Field(default=None)
    filter_: FilterType = Field(default=None)
    colorize: bool | None = Field(default=None)
    serialize: bool | None = Field(default=None)
    backtrace: bool | None = Field(default=None)
    diagnose: bool | None = Field(default=None)
    enqueue: bool | None = Field(default=None)
    context: BaseContext | str | None = Field(default=None)
    catch: bool | None = Field(default=None)
    loop: AbstractEventLoop | None = Field(default=None)
    rotation: RotationType = Field(default=None)
    retention: RetentionType = Field(default=None)
    compression: str | Callable[[str], None] | None = Field(default=None)
    delay: bool | None = Field(default=None)
    watch: bool | None = Field(default=None)
    mode: str | None = Field(default=None)
    buffering: int | None = Field(default=None)
    encoding: str | None = Field(default=None)


__all__ = [
    "HandlerPM",
]
