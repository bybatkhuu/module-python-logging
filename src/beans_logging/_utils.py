import os
import sys
import copy
import errno

from loguru import logger
from pydantic import validate_call

from ._constants import WarnEnum


@validate_call
def create_dir(create_dir: str, warn_mode: WarnEnum = WarnEnum.DEBUG):
    """Create directory if `create_dir` doesn't exist.

    Args:
        create_dir (str, required): Create directory path.
        warn_mode  (str, optional): Warning message mode, for example: 'ERROR', 'ALWAYS', 'DEBUG', 'IGNORE'.
                                        Defaults to "DEBUG".
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


@validate_call
def get_slug_name(file_path: str | None = None) -> str:
    """Slugify the file name from the given file path or the current script's file path.

    Args:
        file_path (str | None, optional): The file path to slugify. If None, uses the current script's file path.
                                            Defaults to None.

    Returns:
        str: The slugified file name.
    """

    if not file_path:
        file_path = sys.argv[0]

    _slug_name = (
        os.path.splitext(os.path.basename(file_path))[0]
        .strip()
        .replace(" ", "-")
        .replace("_", "-")
        .lower()
    )
    return _slug_name


__all__ = [
    "create_dir",
    "deep_merge",
    "get_slug_name",
]
