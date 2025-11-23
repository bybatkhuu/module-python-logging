from typing import cast

from loguru import Record


class CustomRecord(Record):
    level_short: str


def add_level_short(record: Record) -> CustomRecord:
    """Filter for adding short level name to log record.

    Args:
        record (Record, required): Log record as dictionary.

    Returns:
        CustomRecord: Log record as dictionary with short level name.
    """

    if "level_short" not in record:
        record = cast(CustomRecord, record)
        if record["level"].name == "SUCCESS":
            record["level_short"] = "OK"
        elif record["level"].name == "WARNING":
            record["level_short"] = "WARN"
        elif record["level"].name == "CRITICAL":
            record["level_short"] = "CRIT"
        elif 5 < len(record["level"].name):
            record["level_short"] = record["level"].name[:5]
        else:
            record["level_short"] = record["level"].name

    return record


def use_all_filter(record: Record) -> bool:
    """Filter message for all handlers that use this filter.

    Args:
        record (Record): Log record as dictionary.

    Returns:
        bool: False if record is disabled by extra 'disable_all' key, True otherwise.
    """

    record = add_level_short(record)

    if record["extra"].get("disable_all", False):
        return False

    return True


def use_std_filter(record: Record) -> bool:
    """Filter message for std handlers that use this filter.

    Args:
        record (dict): Log record as dictionary.

    Returns:
        bool: False if record is disabled by extra 'disable_std' key, True otherwise.
    """

    if not use_all_filter(record):
        return False

    if record["extra"].get("disable_std", False):
        return False

    return True


def use_file_filter(record: Record) -> bool:
    """Filter message for file handlers that use this filter.

    Args:
        record (Record): Log record as dictionary.

    Returns:
        bool: False if record is disabled by extra 'disable_file' key, True otherwise.
    """

    if not use_all_filter(record):
        return False

    if record["extra"].get("disable_file", False):
        return False

    return True


def use_file_err_filter(record: Record) -> bool:
    """Filter message for error file handlers that use this filter.

    Args:
        record (Record): Log record as dictionary.

    Returns:
        bool: False if record is disabled by extra 'disable_file_err' key, True otherwise.
    """

    if not use_all_filter(record):
        return False

    if record["extra"].get("disable_file_err", False):
        return False

    return True


def use_file_json_filter(record: Record) -> bool:
    """Filter message for json file handlers that use this filter.

    Args:
        record (Record): Log record as dictionary.

    Returns:
        bool: False if record is disabled by extra 'disable_file_json' key, True otherwise.
    """

    if not use_all_filter(record):
        return False

    if record["extra"].get("disable_file_json", False):
        return False

    return True


def use_file_json_err_filter(record: Record) -> bool:
    """Filter message for json error file handlers that use this filter.

    Args:
        record (Record): Log record as dictionary.

    Returns:
        bool: False if record is disabled by extra 'disable_file_json_err' key, True otherwise.
    """

    if not use_all_filter(record):
        return False

    if record["extra"].get("disable_file_json_err", False):
        return False

    return True


__all__ = [
    "add_level_short",
    "use_all_filter",
    "use_std_filter",
    "use_file_filter",
    "use_file_err_filter",
    "use_file_json_filter",
    "use_file_json_err_filter",
]
