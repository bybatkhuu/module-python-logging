from enum import Enum


class HandlerTypeEnum(str, Enum):
    STREAM = "STREAM"
    FILE = "FILE"
    SOCKET = "SOCKET"
    HTTP = "HTTP"
    SYSLOG = "SYSLOG"
    QUEUE = "QUEUE"
    MEMORY = "MEMORY"
    NULL = "NULL"
    CUSTOM = "CUSTOM"


class LogLevelEnum(str, Enum):
    TRACE = "TRACE"
    DEBUG = "DEBUG"
    INFO = "INFO"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


__all__ = [
    "HandlerTypeEnum",
    "LogLevelEnum",
]
