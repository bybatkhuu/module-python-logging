# -*- coding: utf-8 -*-

import json
import traceback


def json_format(record: dict) -> str:
    """Custom json formatter for loguru logger.

    Args:
        record (dict, required): Log record as dictionary.

    Returns:
        str: Format for serialized log record.
    """

    _error = None
    if record["exception"]:
        _error = {}
        _error_type, _error_value, _error_traceback = record["exception"]
        _error["type"] = _error_type.__name__
        _error["value"] = str(_error_value)
        _error["traceback"] = "".join(traceback.format_tb(_error_traceback))

    _extra = None
    if record["extra"] and (0 < len(record["extra"])):
        _extra = record["extra"]

    _json_record = {
        "timestamp": record["time"].strftime("%Y-%m-%dT%H:%M:%S%z"),
        "level": record["level"].name,
        "level_no": record["level"].no,
        "file": record["file"].name,
        "line": record["line"],
        "name": record["name"],
        "process": {"name": record["process"].name, "id": record["process"].id},
        "thread_name": {"name": record["thread"].name, "id": record["thread"].id},
        "message": record["message"],
        "extra": _extra,
        "error": _error,
        "elapsed": str(record["elapsed"]),
    }

    record["serialized"] = json.dumps(_json_record)
    return "{serialized}\n"
