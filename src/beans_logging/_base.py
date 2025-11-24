# Standard libraries
import copy
import logging
from typing import Any, TYPE_CHECKING

# Third-party libraries
if TYPE_CHECKING:
    from loguru import Logger
from loguru import logger
from pydantic import validate_call

# Internal modules
from .__version__ import __version__
from .schemas import LogHandlerPM, LoguruHandlerPM
from .config import LoggerConfigPM
from ._handlers import InterceptHandler


class LoggerLoader:

    @validate_call
    def __init__(
        self,
        config: LoggerConfigPM | dict[str, Any] | None = None,
        auto_load: bool = False,
        **kwargs,
    ) -> None:

        self.handlers_map = {"default.loguru_handler": 0}
        if not config:
            config = LoggerConfigPM()

        self.config = config
        if kwargs:
            self.config = self.config.model_copy(update=kwargs)

        if auto_load:
            self.load()

    def load(self) -> "Logger":
        """Load logger handlers based on logger config.

        Returns:
            Logger: Main loguru logger instance.
        """

        self.remove_handler()
        for _handler in self.config.handlers:
            self.add_handler(_handler)

        self._load_intercept_handlers()

        return logger

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
    ) -> int:

        _handler_id: int
        try:
            if isinstance(handler, dict):
                handler = LogHandlerPM(**handler)
            elif isinstance(handler, LoguruHandlerPM):
                handler = LogHandlerPM(
                    **handler.model_dump(exclude_unset=True, exclude_none=True)
                )

            _handler_id = logger.add(
                **handler.model_dump(
                    exclude_none=True,
                    exclude={
                        "name",
                        "type_",
                        "is_error",
                        "custom_serialize",
                        "enabled",
                    },
                    by_alias=True,
                )
            )
            self.handlers_map[handler.name] = _handler_id

        except Exception:
            logger.critical(f"Failed to add custom log handler to logger!")
            raise

        return _handler_id

    def _load_intercept_handlers(self) -> None:
        """Load intercept handlers to catch third-pary modules log or mute them."""

        _intercept_handler = InterceptHandler()

        # Intercepting all logs from standard (root logger) logging:
        logging.basicConfig(handlers=[_intercept_handler], level=0, force=True)

        _intercepted_modules = set()
        _muted_modules = set()

        if self.config.intercept.enabled:
            for _module_name in list(logging.root.manager.loggerDict.keys()):
                if self.config.intercept.only_base:
                    _module_name = _module_name.split(".")[0]

                if (_module_name not in _intercepted_modules) and (
                    _module_name not in self.config.intercept.ignore_modules
                ):
                    _logger = logging.getLogger(_module_name)
                    _logger.handlers = [_intercept_handler]
                    _logger.propagate = False
                    _intercepted_modules.add(_module_name)

        for _include_module_name in self.config.intercept.include_modules:
            _logger = logging.getLogger(_include_module_name)
            _logger.handlers = [_intercept_handler]
            _logger.propagate = False

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

        return

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
    # ATTRIBUTES


__all__ = [
    "LoggerLoader",
]
