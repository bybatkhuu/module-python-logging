from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from loguru import Record

from .constants import (
    DEFAULT_ALL_STD_HANDLER_NAME,
    DEFAULT_ALL_FILE_HANDLER_NAME,
    DEFAULT_ERR_FILE_HANDLER_NAME,
    DEFAULT_ALL_JSON_HANDLER_NAME,
    DEFAULT_ERR_JSON_HANDLER_NAME,
)


def add_level_short(record: "Record") -> "Record":
    """Filter for adding short level name to log record.

    Args:
        record (Record, required): Log record as dictionary.

    Returns:
        Record: Log record as dictionary with short level name.
    """

    if "level_short" not in record["extra"]:
        if record["level"].name == "SUCCESS":
            record["extra"]["level_short"] = "OK"
        elif record["level"].name == "WARNING":
            record["extra"]["level_short"] = "WARN"
        elif record["level"].name == "CRITICAL":
            record["extra"]["level_short"] = "CRIT"
        elif 5 < len(record["level"].name):
            record["extra"]["level_short"] = record["level"].name[:5]
        else:
            record["extra"]["level_short"] = record["level"].name

    return record


def all_handlers_filter(record: "Record") -> bool:
    """Filter message for all handlers that use this filter.

    Args:
        record (Record): Log record as dictionary.

    Returns:
        bool: False if record is disabled by extra 'disable_all_handlers' key, True otherwise.
    """

    record = add_level_short(record)

    if record["extra"].get("disable_all_handlers", False):
        return False

    return True


def std_filter(record: "Record") -> bool:
    """Filter message for std handlers that use this filter.

    Args:
        record (Record): Log record as dictionary.

    Returns:
        bool: False if record is disabled by extra 'disable_{DEFAULT_ALL_STD_HANDLER_NAME}' key, True otherwise.
    """

    if not all_handlers_filter(record):
        return False

    if record["extra"].get(f"disable_{DEFAULT_ALL_STD_HANDLER_NAME}", False):
        return False

    return True


def file_filter(record: "Record") -> bool:
    """Filter message for file handlers that use this filter.

    Args:
        record (Record): Log record as dictionary.

    Returns:
        bool: False if record is disabled by extra 'disable_{DEFAULT_ALL_FILE_HANDLER_NAME}' key, True otherwise.
    """

    if not all_handlers_filter(record):
        return False

    if record["extra"].get(f"disable_{DEFAULT_ALL_FILE_HANDLER_NAME}", False):
        return False

    return True


def err_file_filter(record: "Record") -> bool:
    """Filter message for error file handlers that use this filter.

    Args:
        record (Record): Log record as dictionary.

    Returns:
        bool: False if record is disabled by extra 'disable_{DEFAULT_ERR_FILE_HANDLER_NAME}' key, True otherwise.
    """

    if not all_handlers_filter(record):
        return False

    if record["extra"].get(f"disable_{DEFAULT_ERR_FILE_HANDLER_NAME}", False):
        return False

    return True


def json_filter(record: "Record") -> bool:
    """Filter message for json file handlers that use this filter.

    Args:
        record (Record): Log record as dictionary.

    Returns:
        bool: False if record is disabled by extra 'disable_{DEFAULT_ALL_JSON_HANDLER_NAME}' key, True otherwise.
    """

    if not all_handlers_filter(record):
        return False

    if record["extra"].get(f"disable_{DEFAULT_ALL_JSON_HANDLER_NAME}", False):
        return False

    return True


def err_json_filter(record: "Record") -> bool:
    """Filter message for json error file handlers that use this filter.

    Args:
        record (Record): Log record as dictionary.

    Returns:
        bool: False if record is disabled by extra 'disable_{DEFAULT_ERR_JSON_HANDLER_NAME}' key, True otherwise.
    """

    if not all_handlers_filter(record):
        return False

    if record["extra"].get(f"disable_{DEFAULT_ERR_JSON_HANDLER_NAME}", False):
        return False

    return True


__all__ = [
    "add_level_short",
    "all_handlers_filter",
    "std_filter",
    "file_filter",
    "err_file_filter",
    "json_filter",
    "err_json_filter",
]
