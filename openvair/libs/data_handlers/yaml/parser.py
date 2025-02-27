"""YAML file parsing utilities.

This module provides helper functions for reading and writing YAML files.

Functions:
    read_yaml: Reads a YAML file and returns its parsed content.
    write_yaml: Writes data to a YAML file.
"""

from typing import Any
from pathlib import Path

import yaml


def read_yaml(file_path: Path) -> Any:  # noqa: ANN401  # YAML can contain various data types (dict, list, str, etc.)
    """Read a YAML file and return its parsed content.

    This function reads a YAML file and safely loads its content. If the file
    is empty, it returns an empty dictionary `{}` instead of `None`.

    Args:
        file_path (Path): The path to the YAML file.

    Returns:
        Any: The parsed YAML data.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        ValueError: If the YAML content contains invalid syntax.
    """
    if not file_path.exists():
        message = f'YAML file not found: {file_path}'
        raise FileNotFoundError(message)

    with file_path.open('r') as f:
        try:
            return yaml.safe_load(f) or {}  # Ensures None is replaced with {}
        except yaml.YAMLError as e:
            message = f'Error reading YAML file {file_path}: {e}'
            raise ValueError(message)


def write_yaml(file_path: Path, data: Any) -> None:  # noqa: ANN401  # YAML can contain various data types (dict, list, str, etc.)
    """Write data to a YAML file.

    This function serializes a Python object into a YAML file. It ensures
    that data is written in a structured manner while preserving key order.

    Args:
        file_path (Path): The path of the YAML file to write to.
        data (Any): The data to serialize into YAML format.

    Raises:
        IOError: If writing to the file fails.
        TypeError: If `data` is not a valid YAML-compatible type.
    """
    with file_path.open('w') as f:
        yaml.dump(data, f, sort_keys=False)
