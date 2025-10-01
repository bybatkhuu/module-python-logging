# -*- coding: utf-8 -*-

import os
import sys
import copy
import errno

from loguru import logger
import pydantic

if "2.0.0" <= pydantic.__version__:
    from pydantic import validate_call
else:
    from pydantic import validate_arguments as validate_call

from ._consts import WarnEnum


@validate_call
def create_dir(create_dir: str, warn_mode: WarnEnum = WarnEnum.DEBUG):
    """Create directory if `create_dir` doesn't exist.

    Args:
        create_dir (str, required): Create directory path.
        warn_mode  (str, optional): Warning message mode, for example: 'ERROR', 'ALWAYS', 'DEBUG', 'IGNORE'. Defaults to "DEBUG".
    """

    if not os.path.isdir(create_dir):
        try:
            _message = f"Creaing '{create_dir}' directory..."
            if warn_mode == WarnEnum.ALWAYS:
                logger.info(_message)
            elif warn_mode == WarnEnum.DEBUG:
                logger.debug(_message)

            os.makedirs(create_dir)
        except OSError as err:
            if err.errno == errno.EEXIST:
                logger.debug(f"'{create_dir}' directory already exists!")
            else:
                logger.error(f"Failed to create '{create_dir}' directory!")
                raise

        _message = f"Successfully created '{create_dir}' directory."
        if warn_mode == WarnEnum.ALWAYS:
            logger.success(_message)
        elif warn_mode == WarnEnum.DEBUG:
            logger.debug(_message)


@validate_call
def deep_merge(dict1: dict, dict2: dict) -> dict:
    """Return a new dictionary that's the result of a deep merge of two dictionaries.
    If there are conflicts, values from `dict2` will overwrite those in `dict1`.

    Args:
        dict1 (dict, required): The base dictionary that will be merged.
        dict2 (dict, required): The dictionary to merge into `dict1`.

    Returns:
        dict: The merged dictionary.
    """

    _merged = copy.deepcopy(dict1)
    for _key, _val in dict2.items():
        if (
            _key in _merged
            and isinstance(_merged[_key], dict)
            and isinstance(_val, dict)
        ):
            _merged[_key] = deep_merge(_merged[_key], _val)
        else:
            _merged[_key] = copy.deepcopy(_val)

    return _merged


def get_default_logs_dir() -> str:
    """Return default logs directory path (current working directory + 'logs').

    Returns:
        str: Default logs directory path.
    """

    return os.path.join(os.getcwd(), "logs")


def get_app_name() -> str:
    """Return application name (sys.argv[0]).

    Returns:
        str: Application name.
    """

    return (
        os.path.splitext(os.path.basename(sys.argv[0]))[0]
        .strip()
        .replace(" ", "-")
        .lower()
    )
