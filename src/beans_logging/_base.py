# -*- coding: utf-8 -*-

## Standard libraries
import os
import copy
import json
import logging
from typing import Union, Dict, Any

## Third-party libraries
import yaml
from loguru import logger
from loguru._logger import Logger
import pydantic

if "2.0.0" <= pydantic.__version__:
    from pydantic import validate_call
else:
    from pydantic import validate_arguments as validate_call

## Internal modules
from ._utils import create_dir, deep_merge
from ._handlers import InterceptHandler
from .rotation import RotationChecker
from .schemas import LoggerConfigPM
from .sinks import std_sink
from .formats import json_format
from .filters import (
    use_all_filter,
    use_std_filter,
    use_file_filter,
    use_file_err_filter,
    use_file_json_filter,
    use_file_json_err_filter,
)


class LoggerLoader:
    """LoggerLoader class for setting up loguru logger.

    Attributes:
        _CONFIG_FILE_PATH (str           ): Default logger config file path. Defaults to '${PWD}/configs/logger.yml'.

        handlers_map      (dict          ): Registered logger handlers map as dictionary. Defaults to None.
        config            (LoggerConfigPM): Logger config as <class 'LoggerConfigPM'>. Defaults to None.
        config_file_path  (str           ): Logger config file path. Defaults to `LoggerLoader._CONFIG_FILE_PATH`.

    Methods:
        load()                      : Load logger handlers based on logger config.
        remove_handler()            : Remove all handlers or specific handler by name or id from logger.
        update_config()             : Update logger config with new config.
        _load_env_vars()            : Load 'BEANS_LOGGING_CONFIG_PATH' environment variable for logger config file path.
        _load_config_file()         : Load logger config from file.
        _check_env()                : Check environment variables for logger config.
        _check_config()             : Check logger config to update some options before loading handlers.
        _add_stream_std_handler()   : Add std stream handler to logger.
        _add_file_log_handler()     : Add log file handler to logger.
        _add_file_err_handler()     : Add error log file handler to logger.
        _add_file_json_handler()    : Add json log file handler to logger.
        _add_file_json_err_handler(): Add json error log file handler to logger.
        add_custom_handler()        : Add custom handler to logger.
        _load_intercept_handlers()  : Load intercept handlers to catch third-pary modules log or mute them.
    """

    _CONFIG_FILE_PATH = os.path.join(os.getcwd(), "configs", "logger.yml")

    @validate_call
    def __init__(
        self,
        config: Union[LoggerConfigPM, Dict[str, Any], None] = None,
        config_file_path: str = _CONFIG_FILE_PATH,
        auto_config_file: bool = True,
        auto_load: bool = False,
    ):
        """LoggerLoader constructor method.

        Args:
            config           (Union[LoggerConfigPM,
                                    dict,
                                    None           ], optional): New logger config to update loaded config. Defaults to None.
            config_file_path (str                   , optional): Logger config file path. Defaults to `LoggerLoader._CONFIG_FILE_PATH`.
            auto_config_file (bool                  , optional): Indicates whether to load logger config file or not. Defaults to True.
            auto_load        (bool                  , optional): Indicates whether to load logger handlers or not. Defaults to False.
        """

        self.handlers_map = {"default": 0}
        self.config = LoggerConfigPM()
        if config:
            self.update_config(config=config)
        self.config_file_path = config_file_path

        self._load_env_vars()

        if auto_config_file:
            self._load_config_file()

        if auto_load:
            self.load()

    def load(self) -> Logger:
        """Load logger handlers based on logger config.

        Returns:
            Logger: Main loguru logger instance.
        """

        self.remove_handler()

        self._check_env()
        self._check_config()

        if self.config.stream.std_handler.enabled:
            self._add_stream_std_handler()

        if self.config.file.log_handlers.enabled:
            self._add_file_log_handler()
            self._add_file_err_handler()

        if self.config.file.json_handlers.enabled:
            self._add_file_json_handler()
            self._add_file_json_err_handler()

        self._load_intercept_handlers()

        return logger

    @validate_call
    def remove_handler(
        self, handler: Union[str, None] = None, handler_type: str = "NAME"
    ):
        """Remove all handlers or specific handler by name or id from logger.

        Raises:
            ValueError: The `handler_type` argument value '{handler_type}' is invalid, must be 'NAME' or 'ID'!

        Args:
            handler      (str, optional): Handler name or id to remove. Defaults to None.
            handler_type (int, optional): Handler type to remove, must be 'NAME' or 'ID'. Defaults to 'name'.
        """

        if handler:
            handler_type = handler_type.strip().upper()
            if handler_type == "NAME":
                if handler in self.handlers_map:
                    _handler_id = self.handlers_map[handler]
                    logger.remove(_handler_id)
                    self.handlers_map.pop(handler)
                    return
            elif handler_type == "ID":
                if handler in self.handlers_map.values():
                    logger.remove(handler)
                    for _handler_name, _handler_id in self.handlers_map.items():
                        if handler == _handler_id:
                            self.handlers_map.pop(_handler_name)
                    return
            else:
                raise ValueError(
                    f"`handler_type` argument value '{handler_type}' is invalid, must be 'NAME' or 'ID'!"
                )

        logger.remove()
        self.handlers_map.clear()

    @validate_call
    def update_config(self, config: Union[LoggerConfigPM, Dict[str, Any]]):
        """Update logger config with new config.

        Args:
            config (Union[LoggerConfigPM, dict], required): New logger config to update loaded config.

        Raises:
            Exception: Failed to load `config` argument into <class 'LoggerConfigPM'>.
        """

        if isinstance(config, dict):
            if "2.0.0" <= pydantic.__version__:
                _config_dict = self.config.model_dump()
            else:
                _config_dict = self.config.dict()

            _merged_dict = deep_merge(_config_dict, config)
            try:
                self.config = LoggerConfigPM(**_merged_dict)
            except Exception:
                logger.critical(
                    "Failed to load `config` argument into <class 'LoggerConfigPM'>."
                )
                raise

        elif isinstance(config, LoggerConfigPM):
            self.config = config

    def _load_env_vars(self):
        """Load 'BEANS_LOGGING_CONFIG_PATH' environment variable for logger config file path."""

        _env_config_file_path = os.getenv("BEANS_LOGGING_CONFIG_PATH")
        if _env_config_file_path:
            try:
                self.config_file_path = _env_config_file_path
            except Exception:
                logger.warning(
                    "Failed to load 'BEANS_LOGGING_CONFIG_PATH' environment variable!"
                )

    def _load_config_file(self):
        """Load logger config from file."""

        _file_format = ""
        if self.config_file_path.lower().endswith((".yml", ".yaml")):
            _file_format = "YAML"
        if self.config_file_path.lower().endswith(".json"):
            _file_format = "JSON"
        # elif self.config_file_path.lower().endswith(".toml"):
        #     _file_format = "TOML"

        ## Loading config from file, if it's exits:
        if os.path.isfile(self.config_file_path):
            if _file_format == "YAML":
                try:
                    with open(
                        self.config_file_path, "r", encoding="utf-8"
                    ) as _config_file:
                        _new_config_dict = yaml.safe_load(_config_file) or {}
                        if "logger" not in _new_config_dict:
                            logger.warning(
                                f"'{self.config_file_path}' YAML config file doesn't have 'logger' section!"
                            )
                            return

                        _new_config_dict = _new_config_dict["logger"]
                        if "2.0.0" <= pydantic.__version__:
                            _config_dict = self.config.model_dump()
                        else:
                            _config_dict = self.config.dict()

                        _merged_dict = deep_merge(_config_dict, _new_config_dict)
                        self.config = LoggerConfigPM(**_merged_dict)
                except Exception:
                    logger.critical(
                        f"Failed to load '{self.config_file_path}' yaml config file."
                    )
                    raise
            elif _file_format == "JSON":
                try:
                    with open(
                        self.config_file_path, "r", encoding="utf-8"
                    ) as _config_file:
                        _new_config_dict = json.load(_config_file) or {}
                        if "logger" not in _new_config_dict:
                            logger.warning(
                                f"'{self.config_file_path}' JSON config file doesn't have 'logger' section!"
                            )
                            return

                        _new_config_dict = _new_config_dict["logger"]
                        if "2.0.0" <= pydantic.__version__:
                            _config_dict = self.config.model_dump()
                        else:
                            _config_dict = self.config.dict()

                        _merged_dict = deep_merge(_config_dict, _new_config_dict)
                        self.config = LoggerConfigPM(**_merged_dict)
                except Exception:
                    logger.critical(
                        f"Failed to load '{self.config_file_path}' json config file."
                    )
                    raise
            # elif _file_format == "TOML":
            #     try:
            #         import toml

            #         with open(
            #             self.config_file_path, "r", encoding="utf-8"
            #         ) as _config_file:
            #             _new_config_dict = toml.load(_config_file) or {}
            #             if "logger" not in _new_config_dict:
            #                 logger.warning(
            #                     f"'{self.config_file_path}' TOML config file doesn't have 'logger' section!"
            #                 )
            #                 return

            #             _new_config_dict = _new_config_dict["logger"]
            #             if "2.0.0" <= pydantic.__version__:
            #                 _config_dict = self.config.model_dump()
            #             else:
            #                 _config_dict = self.config.dict()

            #             _merged_dict = deep_merge(_config_dict, _new_config_dict)
            #             self.config = LoggerConfigPM(**_merged_dict)
            #     except Exception:
            #         logger.critical(
            #             f"Failed to load '{self.config_file_path}' toml config file."
            #         )
            #         raise

    def _check_env(self):
        """Check environment variables for logger config."""

        ## Checking environment for DEBUG option:
        _is_debug = False
        _ENV = str(os.getenv("ENV")).strip().lower()
        _DEBUG = str(os.getenv("DEBUG")).strip().lower()
        if (
            (_DEBUG == "true")
            or (_DEBUG == "1")
            or ((_ENV == "development") and ((_DEBUG == "none") or (_DEBUG == "")))
        ):
            _is_debug = True

        if _is_debug and (self.config.level != "TRACE"):
            self.config.level = "DEBUG"

        if "BEANS_LOGGING_LOGS_DIR" in os.environ:
            self.config.file.logs_dir = os.getenv("BEANS_LOGGING_LOGS_DIR")

        # if self.config.stream.use_color:
        #     ## Checking terminal could support xterm colors:
        #     _TERM = str(os.getenv("TERM")).strip()
        #     if not "xterm" in _TERM:
        #         self.config.stream.use_color = False

    def _check_config(self):
        """Check logger config to update some options before loading handlers."""

        if self.config.level == "TRACE":
            self.config.use_diagnose = True

        if self.config.stream.use_icon:
            self.config.stream.format_str = self.config.stream.format_str.replace(
                "level_short:<5", "level.icon:<4"
            )

        if not os.path.isabs(self.config.file.logs_dir):
            self.config.file.logs_dir = os.path.join(
                os.getcwd(), self.config.file.logs_dir
            )

        if "{app_name}" in self.config.file.log_handlers.log_path:
            self.config.file.log_handlers.log_path = (
                self.config.file.log_handlers.log_path.format(
                    app_name=self.config.app_name
                )
            )

        if "{app_name}" in self.config.file.log_handlers.err_path:
            self.config.file.log_handlers.err_path = (
                self.config.file.log_handlers.err_path.format(
                    app_name=self.config.app_name
                )
            )

        if "{app_name}" in self.config.file.json_handlers.log_path:
            self.config.file.json_handlers.log_path = (
                self.config.file.json_handlers.log_path.format(
                    app_name=self.config.app_name
                )
            )

        if "{app_name}" in self.config.file.json_handlers.err_path:
            self.config.file.json_handlers.err_path = (
                self.config.file.json_handlers.err_path.format(
                    app_name=self.config.app_name
                )
            )

    def _add_stream_std_handler(self) -> int:
        """Add std stream handler to logger.

        Returns:
            int: Handler id.
        """

        return self.add_custom_handler(handler_name="STREAM.STD", filter=use_std_filter)

    def _add_file_log_handler(self) -> int:
        """Add log file handler to logger.

        Returns:
            int: Handler id.
        """

        return self.add_custom_handler(handler_name="FILE", filter=use_file_filter)

    def _add_file_err_handler(self) -> int:
        """Add error log file handler to logger.

        Returns:
            int: Handler id.
        """

        _handler_id = self.add_custom_handler(
            handler_name="FILE_ERR",
            sink=self.config.file.log_handlers.err_path,
            level="WARNING",
            filter=use_file_err_filter,
        )
        return _handler_id

    def _add_file_json_handler(self) -> int:
        """Add json log file handler to logger.

        Returns:
            int: Handler id.
        """

        _kwargs = {
            "sink": self.config.file.json_handlers.log_path,
            "filter": use_file_json_filter,
            "serialize": True,
        }
        if self.config.file.json_handlers.use_custom:
            _kwargs["format"] = json_format
            _kwargs["serialize"] = False

        _handler_id = self.add_custom_handler(handler_name="FILE.JSON", **_kwargs)
        return _handler_id

    def _add_file_json_err_handler(self) -> int:
        """Add json error log file handler to logger.

        Returns:
            int: Handler id.
        """

        _kwargs = {
            "sink": self.config.file.json_handlers.err_path,
            "level": "WARNING",
            "filter": use_file_json_err_filter,
            "serialize": True,
        }
        if self.config.file.json_handlers.use_custom:
            _kwargs["format"] = json_format
            _kwargs["serialize"] = False

        _handler_id = self.add_custom_handler(
            handler_name="FILE.JSON_ERR",
            **_kwargs,
        )
        return _handler_id

    @validate_call
    def add_custom_handler(self, handler_name: str, **kwargs) -> int:
        """Add custom handler to logger.

        Args:
            handler_name (str): Handler name/type to add logger.

        Raises:
            ValueError: Custom handler '{handler_name}' already exists in logger!
            ValueError: The `sink` argument is required for custom handler!

        Returns:
            int: Handler id.
        """

        if handler_name in self.handlers_map:
            raise ValueError(
                f"Custom handler '{handler_name}' already exists in logger!"
            )

        _handler_id = None
        try:
            handler_name = handler_name.strip().upper()

            if "level" not in kwargs:
                kwargs["level"] = self.config.level

            if "filter" not in kwargs:
                kwargs["filter"] = use_all_filter

            if "backtrace" not in kwargs:
                kwargs["backtrace"] = self.config.use_backtrace

            if "diagnose" not in kwargs:
                kwargs["diagnose"] = self.config.use_diagnose

            if handler_name.startswith("STREAM"):
                if "sink" not in kwargs:
                    kwargs["sink"] = std_sink

                if "format" not in kwargs:
                    kwargs["format"] = self.config.stream.format_str

                if "colorize" not in kwargs:
                    kwargs["colorize"] = self.config.stream.use_color
            elif handler_name.startswith("FILE"):
                kwargs["enqueue"] = True

                if "sink" not in kwargs:
                    kwargs["sink"] = self.config.file.log_handlers.log_path

                if isinstance(kwargs["sink"], str):
                    _log_path = kwargs["sink"]
                    if not os.path.isabs(_log_path):
                        _log_path = os.path.abspath(
                            os.path.join(self.config.file.logs_dir, _log_path)
                        )

                    if "{app_name}" in _log_path:
                        _log_path = _log_path.format(app_name=self.config.app_name)

                    _logs_dir, _ = os.path.split(_log_path)
                    create_dir(create_dir=_logs_dir)
                    kwargs["sink"] = _log_path

                if "format" not in kwargs:
                    kwargs["format"] = self.config.file.log_handlers.format_str

                if "rotation" not in kwargs:
                    kwargs["rotation"] = RotationChecker(
                        rotate_size=self.config.file.rotate_size,
                        rotate_time=self.config.file.rotate_time,
                    ).should_rotate

                if "retention" not in kwargs:
                    kwargs["retention"] = self.config.file.backup_count

                if "encoding" not in kwargs:
                    kwargs["encoding"] = self.config.file.encoding

            if "sink" not in kwargs:
                raise ValueError(
                    f"`sink` argument is required for custom handler '{handler_name}'!"
                )

            _handler_id = logger.add(**kwargs)
        except Exception:
            logger.critical(f"Failed to add custom handler '{handler_name}' to logger!")
            raise

        self.handlers_map[handler_name] = _handler_id
        return _handler_id

    def _load_intercept_handlers(self):
        """Load intercept handlers to catch third-pary modules log or mute them."""

        _intercept_handler = InterceptHandler()

        ## Intercepting all logs from standard (root logger) logging:
        logging.basicConfig(handlers=[_intercept_handler], level=0, force=True)

        _intercepted_modules = set()
        _muted_modules = set()

        if self.config.intercept.auto_load.enabled:
            for _module_name in list(logging.root.manager.loggerDict.keys()):
                if self.config.intercept.auto_load.only_base:
                    _module_name = _module_name.split(".")[0]

                if (_module_name not in _intercepted_modules) and (
                    _module_name not in self.config.intercept.auto_load.ignore_modules
                ):
                    _logger = logging.getLogger(_module_name)
                    _logger.handlers = [_intercept_handler]
                    _logger.propagate = False
                    _intercepted_modules.add(_module_name)

        for _include_module_name in self.config.intercept.include_modules:
            _logger = logging.getLogger(_include_module_name)
            _logger.handlers = [_intercept_handler]
            logger.propagate = False

            if _include_module_name not in _intercepted_modules:
                _intercepted_modules.add(_include_module_name)

        for _mute_module_name in self.config.intercept.mute_modules:
            _logger = logging.getLogger(_mute_module_name)
            _logger.handlers = []
            _logger.propagate = False
            _logger.disabled = True

            if _mute_module_name in _intercepted_modules:
                _intercepted_modules.remove(_mute_module_name)

            if _mute_module_name not in _muted_modules:
                _muted_modules.add(_mute_module_name)

        logger.trace(
            f"Intercepted modules: {list(_intercepted_modules)}; Muted modules: {list(_muted_modules)};"
        )

    ### ATTRIBUTES ###
    ## handlers_map ##
    @property
    def handlers_map(self) -> Dict[str, int]:
        try:
            return self.__handlers_map
        except AttributeError:
            self.__handlers_map = {"default": 0}

        return self.__handlers_map

    @handlers_map.setter
    def handlers_map(self, handlers_map: Dict[str, int]):
        if not isinstance(handlers_map, dict):
            raise TypeError(
                f"`handlers_map` attribute type {type(handlers_map)} is invalid, must be <dict>!."
            )

        self.__handlers_map = copy.deepcopy(handlers_map)

    ## handlers_map ##

    ## config ##
    @property
    def config(self) -> LoggerConfigPM:
        try:
            return self.__config
        except AttributeError:
            self.__config = LoggerConfigPM()

        return self.__config

    @config.setter
    def config(self, config: LoggerConfigPM):
        if not isinstance(config, LoggerConfigPM):
            raise TypeError(
                f"`config` attribute type {type(config)} is invalid, must be a <class 'LoggerConfigPM'>!"
            )

        self.__config = copy.deepcopy(config)

    ## config ##

    ## config_file_path ##
    @property
    def config_file_path(self) -> str:
        try:
            return self.__config_file_path
        except AttributeError:
            self.__config_file_path = LoggerLoader._CONFIG_FILE_PATH

        return self.__config_file_path

    @config_file_path.setter
    def config_file_path(self, config_file_path: str):
        if not isinstance(config_file_path, str):
            raise TypeError(
                f"`config_file_path` attribute type {type(config_file_path)} is invalid, must be a <str>!"
            )

        config_file_path = config_file_path.strip()
        if config_file_path == "":
            raise ValueError("`config_file_path` attribute value is empty!")

        if (not config_file_path.lower().endswith((".yml", ".yaml"))) and (
            not config_file_path.lower().endswith(".json")
        ):
            if not config_file_path.lower().endswith(".toml"):
                raise NotImplementedError(
                    f"`config_file_path` attribute value '{config_file_path}' is invalid, TOML file format is not supported yet!"
                )

            raise ValueError(
                f"`config_file_path` attribute value '{config_file_path}' is invalid, file must be '.yml', '.yaml' or '.json' format!"
            )

        if not os.path.isabs(config_file_path):
            config_file_path = os.path.join(os.getcwd(), config_file_path)

        self.__config_file_path = config_file_path

    ## config_file_path ##
    ### ATTRIBUTES ###
