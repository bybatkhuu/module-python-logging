import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from loguru import Message


def std_sink(message: "Message") -> None:
    """Print message based on log level to stdout or stderr.

    Args:
        message (Message, required): Log message.
    """

    if message.record["level"].no < 40:
        sys.stdout.write(message)
    else:
        sys.stderr.write(message)

    return


__all__ = ["std_sink"]
