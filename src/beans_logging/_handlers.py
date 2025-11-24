import inspect
import logging
from logging import LogRecord, Handler

from loguru import logger


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


class PropagateHandler(Handler):
    """A handler class that propagates logs to the appropriate logger in standard logging.

    Args:
        Handler: Handler class from standard logging.
    """

    def emit(self, record: LogRecord) -> None:
        """Handle propagated log record to the appropriate logger.

        Args:
            record (LogRecord, required): Log needs to be handled.
        """

        logging.getLogger(record.name).handle(record)
        return


__all__ = [
    "InterceptHandler",
    "PropagateHandler",
]
