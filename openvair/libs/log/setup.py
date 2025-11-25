"""Logging setup utilities.

This module provides functions for setting up logging configurations
from a TOML configuration file. If the file is not found or is invalid,
a basic logging setup is applied.

Functions:
    setup_logging: Configures logging based on a TOML configuration file.
    _base_setup_logging: Applies a basic logging setup if configuration
        file loading fails.
"""

import logging.config
from pathlib import Path

import toml


def _base_setup_logging() -> None:
    """Apply a basic logging configuration.

    This function sets up a simple logging configuration that outputs
    logs to the console with a default format. It is used as a fallback
    if the TOML configuration file cannot be loaded.
    """
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        fmt='(%(asctime)s) (%(name)s) (%(levelname)s) > %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )
    console_handler.setFormatter(formatter)

    logging.basicConfig(level=10, handlers=[console_handler])
    logging.getLogger('pika').setLevel('CRITICAL')


def setup_logging(
    log_config_path: Path,
) -> None:
    """Set up logging from a TOML configuration file.

    This function attempts to configure logging using a TOML configuration
    file. If the file does not exist or contains invalid data, it applies
    a basic logging configuration instead.

    Args:
        log_config_path (str): The path to the TOML configuration file
            for logging.

    Returns:
        None
    """
    if log_config_path.exists():
        try:
            config = toml.load(log_config_path)
            logging.config.dictConfig(config)
        except ValueError:
            _base_setup_logging()
        finally:
            logging.getLogger('pika').setLevel('CRITICAL')
    else:
        _base_setup_logging()
