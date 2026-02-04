import json
import traceback
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from loguru import Record
else:
    from .typing import Record


def json_format(record: "Record") -> str:
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
        if _error_type:
            _error["type"] = _error_type.__name__
        else:
            _error["type"] = "None"

        _error["value"] = str(_error_value)
        _error["traceback"] = "".join(traceback.format_tb(_error_traceback))

    _extra = None
    if record["extra"] and (0 < len(record["extra"])):
        _extra = record["extra"]

    if _extra and ("serialized" in _extra):
        del _extra["serialized"]

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

    record["extra"]["serialized"] = json.dumps(_json_record)
    return "{extra[serialized]}\n"


__all__ = [
    "json_format",
]
