from pydantic import validate_call
from loguru import logger

from potato_util.constants import WarnEnum

from .constants import LogLevelEnum


@validate_call
def log_at(
    message: str,
    level: LogLevelEnum | str = LogLevelEnum.INFO,
    warn_mode: WarnEnum | str = WarnEnum.ALWAYS,
) -> None:
    """Log message with level and warn mode.

    Args:
        message   (str               , reqiured): Message to log.
        level     (LogLevelEnum | str, optional): Log level when warn mode is `WarnEnum.ALWAYS`.
                                                    Defaults to `LogLevelEnum.INFO`.
        warn_mode (WarnEnum | str    , optional): Warn mode to use. Defaults to `WarnEnum.ALWAYS`.

    Raises:
        ValueError: If `level` is not a valid log level.
        ValueError: If `warn_mode` is not a valid warn mode.
    """

    if isinstance(level, str):
        level = LogLevelEnum(level.strip().upper())

    if isinstance(warn_mode, str):
        warn_mode = WarnEnum(warn_mode.strip().upper())

    _logger = logger.opt(depth=3)
    if warn_mode == WarnEnum.ALWAYS:
        if level == LogLevelEnum.INFO:
            _logger.info(message)
        elif level == LogLevelEnum.SUCCESS:
            _logger.success(message)
        elif level == LogLevelEnum.WARNING:
            _logger.warning(message)
        elif level == LogLevelEnum.ERROR:
            _logger.error(message)
        elif level == LogLevelEnum.CRITICAL:
            _logger.critical(message)
        elif level == LogLevelEnum.TRACE:
            _logger.trace(message)

    elif warn_mode == WarnEnum.DEBUG:
        _logger.debug(message)

    return


__all__ = [
    "log_at",
]
