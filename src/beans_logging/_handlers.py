import logging
from logging import LogRecord, Handler


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
    "PropagateHandler",
]
