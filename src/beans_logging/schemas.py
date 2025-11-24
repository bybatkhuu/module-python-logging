import os
import uuid
import inspect
import logging
import datetime
from pathlib import Path
from asyncio import AbstractEventLoop
from multiprocessing.context import BaseContext
from typing import TYPE_CHECKING, Any, TextIO, Union, Protocol, runtime_checkable
from typing_extensions import Self
from collections.abc import Callable, Awaitable

if TYPE_CHECKING:
    from loguru import Record, Message
from pydantic import BaseModel, Field, ConfigDict, model_validator

from ._constants import LogHandlerTypeEnum, LogLevelEnum


class ExtraBaseModel(BaseModel):
    model_config = ConfigDict(
        extra="allow",
        validate_default=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )


@runtime_checkable
class _SupportsWrite(Protocol):
    def write(self, __s: str) -> Any: ...
    def flush(self) -> Any: ...


_SinkType = Union[
    str,
    Path,
    TextIO,
    _SupportsWrite,
    Callable[[Any], Any],
    Callable[[Any], Awaitable[Any]],
    logging.Handler,
]


class LoguruHandlerPM(ExtraBaseModel):
    sink: _SinkType = Field(...)
    level: str | int | None = Field(default=None)
    format_: str | Callable[["Record"], str] | None = Field(
        default=None, serialization_alias="format"
    )
    filter_: Callable[["Record"], bool] | str | dict[str, Any] | None = Field(
        default=None, serialization_alias="filter"
    )
    colorize: bool | None = Field(default=None)
    serialize: bool | None = Field(default=None)
    backtrace: bool | None = Field(default=None)
    diagnose: bool | None = Field(default=None)
    enqueue: bool | None = Field(default=None)
    context: BaseContext | str | None = Field(default=None)
    catch: bool | None = Field(default=None)
    loop: AbstractEventLoop | None = Field(default=None)
    rotation: (
        str
        | int
        | datetime.time
        | datetime.timedelta
        | Callable[[str, Any], bool]
        | Callable[["Message", TextIO], bool]
        | None
    ) = Field(default=None)
    retention: str | int | datetime.timedelta | Callable[[Any], None] | None = Field(
        default=None
    )
    compression: str | Callable[[str], None] | None = Field(default=None)
    delay: bool | None = Field(default=None)
    watch: bool | None = Field(default=None)
    mode: str | None = Field(default=None)
    buffering: int | None = Field(default=None)
    encoding: str | None = Field(default=None)


class LogHandlerPM(LoguruHandlerPM):
    name: str = Field(default_factory=lambda: f"log_handler.{uuid.uuid4().hex}")
    type_: LogHandlerTypeEnum = Field(default=LogHandlerTypeEnum.UNKNOWN)
    sink: _SinkType | None = Field(default=None)
    level: str | int | LogLevelEnum | None = Field(default=None)
    is_error: bool = Field(default=False)
    custom_serialize: bool = Field(default=False)
    enabled: bool = Field(default=True)

    @model_validator(mode="after")
    def _check_all(self) -> Self:

        if (self.loop is not None) and (
            (not callable(self.sink)) or (not inspect.iscoroutinefunction(self.sink))
        ):
            raise ValueError(
                f"'loop' attribute is set but 'sink' attribute type {type(self.sink)} is invalid, 'loop' only can be used with async callable (coroutine function) 'sink'!"
            )

        if not isinstance(self.sink, (str, os.PathLike)):
            for _attr in (
                "rotation",
                "retention",
                "compression",
                "delay",
                "watch",
                "mode",
                "buffering",
                "encoding",
            ):
                if getattr(self, _attr) is not None:
                    raise ValueError(
                        f"'{_attr}' attribute is set but 'sink' attribute type {type(self.sink).__name__} is invalid, '{_attr}' can only be used with file path 'sink'!"
                    )

        return self


__all__ = [
    "ExtraBaseModel",
    "LoguruHandlerPM",
    "LogHandlerPM",
]
