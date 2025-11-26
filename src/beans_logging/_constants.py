from enum import Enum


class LogHandlerTypeEnum(str, Enum):
    STD = "STD"
    FILE = "FILE"
    SOCKET = "SOCKET"
    HTTP = "HTTP"
    SYSLOG = "SYSLOG"
    QUEUE = "QUEUE"
    MEMORY = "MEMORY"
    NULL = "NULL"
    CUSTOM = "CUSTOM"
    UNKNOWN = "UNKNOWN"


class LogLevelEnum(str, Enum):
    TRACE = "TRACE"
    DEBUG = "DEBUG"
    INFO = "INFO"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


__all__ = [
    "LogHandlerTypeEnum",
    "LogLevelEnum",
]
