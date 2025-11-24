import inspect
import logging
from logging import LogRecord, Handler

from loguru import logger
from pydantic import validate_call

from .config import LoggerConfigPM


class InterceptHandler(Handler):
    """A handler class that intercepts logs from standard logging and redirects them to loguru logger.

    Inherits:
        Handler: Handler class from standard logging.

    Overrides:
        emit(): Handle intercepted log record.
    """

    def emit(self, record: LogRecord) -> None:
        """Handle intercepted log record.

        Args:
            record (LogRecord, required): Log needs to be handled.
        """

        # Get corresponding Loguru level if it exists.
        try:
            _level: str | int = logger.level(record.levelname).name
        except ValueError:
            _level = record.levelno

        # Find caller from where originated the logged message.
        _frame, _depth = inspect.currentframe(), 0
        while _frame and (_depth == 0 or _frame.f_code.co_filename == logging.__file__):
            _frame = _frame.f_back
            _depth += 1

        logger.opt(depth=_depth, exception=record.exc_info).log(
            _level, record.getMessage()
        )

        return


@validate_call
def init_intercepter(config: LoggerConfigPM) -> None:

    _intercept_handler = InterceptHandler()

    # Intercepting all logs from standard (root logger) logging:
    logging.basicConfig(handlers=[_intercept_handler], level=0, force=True)

    _intercepted_modules = set()
    _muted_modules = set()

    if config.intercept.enabled:
        for _module_name in list(logging.root.manager.loggerDict.keys()):
            if config.intercept.only_base:
                _module_name = _module_name.split(".")[0]

            if (_module_name not in _intercepted_modules) and (
                _module_name not in config.intercept.ignore_modules
            ):
                _logger = logging.getLogger(_module_name)
                _logger.handlers = [_intercept_handler]
                _logger.propagate = False
                _intercepted_modules.add(_module_name)

    for _include_module_name in config.intercept.include_modules:
        _logger = logging.getLogger(_include_module_name)
        _logger.handlers = [_intercept_handler]
        _logger.propagate = False

        if _include_module_name not in _intercepted_modules:
            _intercepted_modules.add(_include_module_name)

    for _mute_module_name in config.intercept.mute_modules:
        _logger = logging.getLogger(_mute_module_name)
        _logger.handlers = []
        _logger.propagate = False
        _logger.disabled = True

        if _mute_module_name in _intercepted_modules:
            _intercepted_modules.remove(_mute_module_name)

        if _mute_module_name not in _muted_modules:
            _muted_modules.add(_mute_module_name)

    logger.trace(
        f"Intercepted modules: {list(_intercepted_modules)}; Muted modules: {list(_muted_modules)};"
    )

    return


__all__ = [
    "InterceptHandler",
    "init_intercepter",
]
