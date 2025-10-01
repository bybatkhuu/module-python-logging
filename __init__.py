# flake8: noqa

try:
    from .src.beans_logging import *
except ImportError:
    from src.beans_logging import *
