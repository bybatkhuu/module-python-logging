import pytest

from beans_logging import Logger, LoggerConfigPM, LoggerLoader


@pytest.fixture
def logger_loader():
    _logger_loader = LoggerLoader()

    yield _logger_loader

    del _logger_loader


@pytest.fixture
def logger():
    from beans_logging import logger

    yield logger

    del logger


def test_init(logger: Logger, logger_loader: LoggerLoader):
    logger.info("Testing initialization of 'LoggerLoader'...")

    assert isinstance(logger_loader, LoggerLoader)
    assert logger_loader.handlers_map == {"default": 0}
    assert logger_loader.config_file_path == LoggerLoader._CONFIG_FILE_PATH
    assert isinstance(logger_loader.config, LoggerConfigPM)

    logger.success("Done: Initialization of 'LoggerLoader'.\n")


def test_load(logger: Logger, logger_loader: LoggerLoader):
    logger.info("Testing 'load' method of 'LoggerLoader'...")

    logger_loader.update_config(config={"level": "TRACE"})
    _logger: Logger = logger_loader.load()

    assert isinstance(_logger, Logger)
    assert _logger == logger
    _logger.trace("Tracing...")
    _logger.debug("Debugging...")
    _logger.info("Logging info.")
    _logger.success("Success.")
    _logger.warning("Warning something.")
    _logger.error("Error occured.")
    _logger.critical("CRITICAL ERROR.")

    logger.success("Done: 'load' method.\n")


def test_methods(logger: Logger):
    logger.info("Testing 'logger' methods...")

    logger.trace("Tracing...")
    logger.debug("Debugging...")
    logger.info("Logging info.")
    logger.success("Success.")
    logger.warning("Warning something.")
    logger.error("Error occured.")
    logger.critical("CRITICAL ERROR.")

    logger.success("Done: 'logger' methods.\n")
