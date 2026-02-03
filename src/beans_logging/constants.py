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


DEFAULT_LOGURU_HANDLER_NAME = "default.loguru.handler"
DEFAULT_ALL_STD_HANDLER_NAME = "default.all.std_handler"
DEFAULT_ALL_FILE_HANDLER_NAME = "default.all.file_handler"
DEFAULT_ERR_FILE_HANDLER_NAME = "default.err.file_handler"
DEFAULT_ALL_JSON_HANDLER_NAME = "default.all.json_handler"
DEFAULT_ERR_JSON_HANDLER_NAME = "default.err.json_handler"
DEFAULT_NO_HANDLER_NAME_PREFIX = "log_handler."


__all__ = [
    "LogHandlerTypeEnum",
    "LogLevelEnum",
    "DEFAULT_LOGURU_HANDLER_NAME",
    "DEFAULT_ALL_STD_HANDLER_NAME",
    "DEFAULT_ALL_FILE_HANDLER_NAME",
    "DEFAULT_ERR_FILE_HANDLER_NAME",
    "DEFAULT_ALL_JSON_HANDLER_NAME",
    "DEFAULT_ERR_JSON_HANDLER_NAME",
    "DEFAULT_NO_HANDLER_NAME_PREFIX",
]
