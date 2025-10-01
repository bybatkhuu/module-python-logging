# -*- coding: utf-8 -*-

import sys

from loguru._handler import Message


def std_sink(message: Message):
    """Print message based on log level to stdout or stderr.

    Args:
        message (Message, required): Log message.
    """

    if message.record["level"].no < 40:
        sys.stdout.write(message)
    else:
        sys.stderr.write(message)
