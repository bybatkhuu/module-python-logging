# Standard libraries
import os
import copy
from pathlib import Path
from typing import Any, TYPE_CHECKING

# Third-party libraries
import potato_util as utils

if TYPE_CHECKING:
    from loguru import Logger
else:
    from loguru._logger import Logger
from loguru import logger
from pydantic import validate_call
from potato_util import io as io_utils

# Internal modules
from .schemas import LogHandlerPM, LoguruHandlerPM
from .config import LoggerConfigPM
from ._builder import build_handler
from ._intercept import init_intercepter


class LoggerLoader:

    _CONFIG_PATH = os.path.join(os.getcwd(), "configs", "logger.yml")

    @validate_call
    def __init__(
        self,
        config: LoggerConfigPM | dict[str, Any] | None = None,
        config_path: str | None = _CONFIG_PATH,
        auto_load: bool = False,
        **kwargs,
    ) -> None:

        self.handlers_map = {"default.loguru_handler": 0}
        if not config:
            config = LoggerConfigPM()

        self.config = config
        if kwargs:
            self.update_config(config=kwargs)

        self.config_path = config_path

        if auto_load:
            self.load()

    def load(self) -> "Logger":
        """Load logger handlers based on logger config.

        Returns:
            Logger: Main loguru logger instance.
        """

        self.remove_handler()
        self._load_config_file()

        for _handler in self.config.handlers:
            self.add_handler(_handler)

        init_intercepter(config=self.config)
        return logger

    def _load_config_file(self) -> None:

        if self.config_path and os.path.isfile(self.config_path):
            _config_data = io_utils.read_config_file(config_path=self.config_path)
            if _config_data and ("logger" in _config_data):
                _config_data = _config_data.get("logger", {})
                if _config_data:
                    self.update_config(config=_config_data)

        return

    @validate_call
    def update_config(self, config: LoggerConfigPM | dict[str, Any]) -> None:

        if isinstance(config, dict):
            _config_dict = self.config.model_dump()
            _merged_dict = utils.deep_merge(_config_dict, config)
            try:
                self.config = LoggerConfigPM(**_merged_dict)
            except Exception:
                logger.critical(
                    "Failed to load `config` argument into <class 'LoggerConfigPM'>."
                )
                raise

        elif isinstance(config, LoggerConfigPM):
            self.config = config

        return

    @validate_call
    def remove_handler(self, handler: str | int | None = None) -> None:

        if handler:
            if isinstance(handler, str):
                if handler in self.handlers_map:
                    _handler_id = self.handlers_map.get(handler)
                    logger.remove(_handler_id)
                    self.handlers_map.pop(handler)
                else:
                    raise ValueError(
                        f"Not found handler name '{handler}' in handlers map!"
                    )

            elif isinstance(handler, int):
                if handler in self.handlers_map.values():
                    logger.remove(handler)
                    for _handler_name, _handler_id in self.handlers_map.items():
                        if handler == _handler_id:
                            self.handlers_map.pop(_handler_name)
                            break
                else:
                    raise ValueError(
                        f"Not found handler ID '{handler}' in handlers map!"
                    )
        else:
            logger.remove()
            self.handlers_map.clear()

        return

    @validate_call
    def add_handler(
        self, handler: LogHandlerPM | LoguruHandlerPM | dict[str, Any]
    ) -> int | None:

        _handler_id: int | None = None
        try:
            if isinstance(handler, dict):
                handler = LogHandlerPM(**handler)
            elif isinstance(handler, LoguruHandlerPM):
                handler = LogHandlerPM(
                    **handler.model_dump(exclude_unset=True, exclude_none=True)
                )

            _handler_dict = build_handler(handler=handler, config=self.config)
            if handler.enabled:
                _sink = _handler_dict.get("sink")
                if isinstance(_sink, (str, Path)):
                    _logs_dir = os.path.dirname(_sink)
                    if _logs_dir:
                        io_utils.create_dir(create_dir=_logs_dir)

            _handler_id = logger.add(**_handler_dict)
            self.handlers_map[handler.name] = _handler_id

        except Exception:
            logger.critical(f"Failed to add custom log handler to logger!")
            raise

        return _handler_id

    # ATTRIBUTES
    # handlers_map
    @property
    def handlers_map(self) -> dict[str, int]:
        try:
            return self.__handlers_map
        except AttributeError:
            self.__handlers_map = {"default.loguru_handler": 0}

        return self.__handlers_map

    @handlers_map.setter
    def handlers_map(self, handlers_map: dict[str, int]) -> None:
        if not isinstance(handlers_map, dict):
            raise TypeError(
                f"`handlers_map` attribute type {type(handlers_map)} is invalid, must be <dict>!."
            )

        self.__handlers_map = copy.deepcopy(handlers_map)
        return

    # handlers_map

    # config
    @property
    def config(self) -> LoggerConfigPM:
        try:
            return self.__config
        except AttributeError:
            self.__config = LoggerConfigPM()

        return self.__config

    @config.setter
    def config(self, config: LoggerConfigPM | dict[str, Any]) -> None:
        if (not isinstance(config, LoggerConfigPM)) and (not isinstance(config, dict)):
            raise TypeError(
                f"`config` attribute type {type(config)} is invalid, must be a <class 'LoggerConfigPM'> or <dict>!"
            )

        if isinstance(config, dict):
            config = LoggerConfigPM(**config)
        elif isinstance(config, LoggerConfigPM):
            config = config.model_copy(deep=True)

        self.__config = config
        return

    # config

    # config_file_path
    @property
    def config_file_path(self) -> str:
        try:
            return self.__config_file_path
        except AttributeError:
            self.__config_file_path = LoggerLoader._CONFIG_PATH

        return self.__config_file_path

    @config_file_path.setter
    def config_file_path(self, config_file_path: str) -> None:
        if not isinstance(config_file_path, str):
            raise TypeError(
                f"`config_file_path` attribute type {type(config_file_path)} is invalid, must be a <str>!"
            )

        config_file_path = config_file_path.strip()
        if config_file_path == "":
            raise ValueError("`config_file_path` attribute value is empty!")

        if (
            (not config_file_path.lower().endswith((".yml", ".yaml")))
            and (not config_file_path.lower().endswith(".json"))
            and (not config_file_path.lower().endswith(".toml"))
        ):
            raise ValueError(
                f"`config_file_path` attribute value '{config_file_path}' is invalid, "
                f"file must be '.yml', '.yaml', '.json' or '.toml' format!"
            )

        self.__config_file_path = config_file_path

    # config_file_path
    # ATTRIBUTES


__all__ = [
    "LoggerLoader",
]
