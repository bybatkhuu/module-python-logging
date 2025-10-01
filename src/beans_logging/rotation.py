# -*- coding: utf-8 -*-

import datetime
from typing import TextIO

from loguru._handler import Message


class RotationChecker:
    """RotationChecker class for checking file size and time for rotation.

    Attributes:
        _size_limit  (int              ): File size limit for rotation.
        _dtime_limit (datetime.datetime): Datetime when the log file should rotate.

    Methods:
        should_rotate(): Check if the log file should rotate.
    """

    def __init__(self, *, rotate_size: int, rotate_time: datetime.time):
        """RotationChecker constructor method.

        Args:
            rotate_size (int,           required): File size limit for rotation.
            rotate_time (datetime.time, required): Time when the log file should rotate.
        """

        _current_dtime = datetime.datetime.now()

        self._size_limit = rotate_size
        self._dtime_limit = _current_dtime.replace(
            hour=rotate_time.hour,
            minute=rotate_time.minute,
            second=rotate_time.second,
        )

        if _current_dtime >= self._dtime_limit:
            ## The current time is already past the target time so it would rotate already.
            ## Add one day to prevent an immediate rotation.
            self._dtime_limit += datetime.timedelta(days=1)

    def should_rotate(self, message: Message, file: TextIO) -> bool:
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
            message.record["time"].timestamp() - self._dtime_limit.timestamp()
        )
        if _elapsed_timestamp >= 0:
            _elapsed_days = datetime.timedelta(seconds=_elapsed_timestamp).days
            self._dtime_limit += datetime.timedelta(days=_elapsed_days + 1)
            return True

        return False
