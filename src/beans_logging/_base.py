# Standard libraries
from typing import Any

# Third-party libraries
from pydantic import validate_call

# Internal modules
from .config import LoggerConfigPM
from .__version__ import __version__


class LoggerLoader:

    @validate_call
    def __init__(
        self,
        config: LoggerConfigPM | dict[str, Any] | None = None,
        auto_run: bool = False,
        **kwargs,
    ) -> None:
        pass


__all__ = [
    "LoggerLoader",
]
