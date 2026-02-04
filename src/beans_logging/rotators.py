import datetime
from typing import TextIO, TYPE_CHECKING

if TYPE_CHECKING:
    from loguru import Message
else:
    from ._typing import Message


class Rotator:
    """Rotator class for checking file size and time for rotation.

    Attributes:
        _size_limit (int              ): File size limit for rotation.
        _dt_limit   (datetime.datetime): Datetime when the log file should rotate.

    Methods:
        should_rotate(): Check if the log file should rotate.
    """

    def __init__(self, *, rotate_size: int, rotate_time: datetime.time):
        """Rotator constructor method.

        Args:
            rotate_size (int,           required): File size limit for rotation.
            rotate_time (datetime.time, required): Time when the log file should rotate.
        """

        _current_dt = datetime.datetime.now()

        self._size_limit = rotate_size
        self._dt_limit = _current_dt.replace(
            hour=rotate_time.hour,
            minute=rotate_time.minute,
            second=rotate_time.second,
        )

        if _current_dt >= self._dt_limit:
            # The current time is already past the target time so it would rotate already.
            # Add one day to prevent an immediate rotation.
            self._dt_limit += datetime.timedelta(days=1)

    def should_rotate(self, message: "Message", file: TextIO) -> bool:
        """Check if the log file should rotate.

        Args:
            message (Message, required): The message to be logged.
            file    (TextIO,  required): The file to be logged.

        Returns:
            bool: True if the log file should rotate, False otherwise.
        """

        file.seek(0, 2)
        if file.tell() + len(message) > self._size_limit:
            return True

        _elapsed_timestamp = (
            message.record["time"].timestamp() - self._dt_limit.timestamp()
        )
        if _elapsed_timestamp >= 0:
            _elapsed_days = datetime.timedelta(seconds=_elapsed_timestamp).days
            self._dt_limit += datetime.timedelta(days=_elapsed_days + 1)
            return True

        return False


__all__ = [
    "Rotator",
]
