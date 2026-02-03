# flake8: noqa

try:
    from .src.beans_logging.auto import *
except ImportError:
    from src.beans_logging.auto import *  # type: ignore
