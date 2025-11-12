from pathlib import Path

from pydantic import Field
from potato_util import get_slug_name

from .schema import ExtraBaseModel, HandlerPM


def _get_logs_dir() -> Path:
    _logs_dir = Path.cwd() / "logs"
    # os.makedirs(_logs_dir, exist_ok=True)
    return _logs_dir


def _get_default_handlers(app_name: str) -> list[HandlerPM]:
    return []


class ExtraConfigPM(ExtraBaseModel):
    pass


class LoggerConfigPM(ExtraBaseModel):
    app_name: str = Field(default_factory=get_slug_name, min_length=1, max_length=128)
    logs_dir: str | Path = Field(default_factory=_get_logs_dir)
    handlers: list[HandlerPM] = Field(default=[])
    extra: ExtraConfigPM | None = Field(default_factory=ExtraConfigPM)


__all__ = [
    "LoggerConfigPM",
]
