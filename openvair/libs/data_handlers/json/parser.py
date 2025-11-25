"""JSON file parsing utilities.

This module provides helper functions for reading and writing JSON files.

Functions:
    read_json: Reads a JSON file and returns its parsed content.
    write_json: Writes data to a JSON file.
"""

import json
from typing import Any
from pathlib import Path


def read_json(file_path: Path) -> Any:  # noqa: ANN401  # JSON can contain various data types (dict, list, str, etc.)
    """Read a JSON file and return its parsed content.

    Args:
        file_path (Path): The path to the JSON file.

    Returns:
        Any: Parsed JSON data (usually a dict or list).

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the JSON content is invalid.
    """
    if not file_path.exists():
        message = f'JSON file not found: {file_path}'
        raise FileNotFoundError(message)

    with file_path.open('r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError as e:
            message = f'Error reading JSON file {file_path}: {e}'
            raise ValueError(message)


def write_json(file_path: Path, data: Any, indent: int = 4) -> None:  # noqa: ANN401  # JSON can contain various data types (dict, list, str, etc.)
    """Write data to a JSON file.

    Args:
        file_path (Path): The path of the JSON file to write.
        data (Any): The data to serialize into JSON.
        indent (int, optional): Indentation level for pretty-printing. Defaults
            to 4.

    Raises:
        IOError: If writing to the file fails.
    """
    with file_path.open('w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)
