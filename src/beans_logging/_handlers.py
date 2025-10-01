# -*- coding: utf-8 -*-

import sys
import logging
from logging import LogRecord

from loguru import logger


class InterceptHandler(logging.Handler):
    """A handler class that intercepts logs from standard logging and redirects them to loguru logger.

    Inherits:
        logging.Handler: Handler class from standard logging.

    Overrides:
        emit(): Handle intercepted log record.
    """

    def emit(self, record: LogRecord):
        """
        Handle intercepted log record.

        Args:
            record (LogRecord, required): Log needs to be handled.
        """

        ## Get corresponding Loguru level if it exists
        try:
            _level = logger.level(record.levelname).name
        except ValueError:
            _level = record.levelno

        ## Find caller from where originated the logged message
        _frame, _depth = sys._getframe(6), 6
        while _frame and _frame.f_code.co_filename == logging.__file__:
            _frame = _frame.f_back
            _depth += 1

        logger.opt(depth=_depth, exception=record.exc_info).log(
            _level, record.getMessage()
        )
