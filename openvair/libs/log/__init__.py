"""Logging module initialization.

This module provides a `get_logger` function to retrieve a configured logger
instance. The logger is set up based on a configuration file, which is
typically in TOML format.

Functions:
    get_logger: Returns a logger instance configured according to the
        provided or default configuration file.
"""

import logging
from pathlib import Path

from openvair.libs.log.setup import setup_logging
from openvair.libs.client.config import get_sentry_dsn

toml_path = Path(__file__).parent / 'logging_config.toml'


def get_logger(
    name: str,
    config_path: Path = toml_path,
) -> logging.Logger:
    """Get a logger instance with the specified name.

    This function initializes the logger using settings from a TOML
    configuration file. If the configuration file is not found, it falls
    back to a basic logging setup.

    Args:
        name (str): The name of the logger. It's common practice to use
            `__name__` for the logger name.
        config_path (str): The path to the TOML configuration file for
            logger settings. Defaults to `logging_config.toml` in the log
            package directory.

    Returns:
        logging.Logger: An initialized logger instance configured according
        to the specified or default configuration file.
    """
    get_sentry_dsn()
    setup_logging(log_config_path=config_path)
    return logging.getLogger(name)
