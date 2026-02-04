from datetime import datetime, timedelta
from types import TracebackType
from typing import Any, NamedTuple, TypedDict


class _RecordAttribute:
    def __format__(self, spec: str) -> str: ...


class RecordFile(_RecordAttribute):
    name: str
    path: str


class RecordLevel(_RecordAttribute):
    name: str
    no: int
    icon: str


class RecordThread(_RecordAttribute):
    id: int
    name: str


class RecordProcess(_RecordAttribute):
    id: int
    name: str


class RecordException(NamedTuple):
    type: type[BaseException] | None
    value: BaseException | None
    traceback: TracebackType | None


class Record(TypedDict):
    elapsed: timedelta
    exception: RecordException | None
    extra: dict[Any, Any]
    file: RecordFile
    function: str
    level: RecordLevel
    line: int
    message: str
    module: str
    name: str | None
    process: RecordProcess
    thread: RecordThread
    time: datetime


class Message(str):
    record: Record


__all__ = [
    "Record",
    "Message",
]
