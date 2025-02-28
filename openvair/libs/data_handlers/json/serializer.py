"""JSON serialization utilities.

This module provides functions for serializing and deserializing JSON-compatible
data structures.

Functions:
    serialize_json: Serializes data into a JSON-formatted string.
    deserialize_json: Deserializes a JSON-formatted string into a Python object.
"""

import json
from typing import Any


def serialize_json(data: Any, indent: int = 4) -> str:  # noqa: ANN401  # JSON can contain various data types (dict, list, str, etc.)
    """Serialize data into a JSON-formatted string.

    Args:
        data (Any): The data to convert.
        indent (int, optional): Indentation level for pretty-printing. Defaults
            to 4.

    Returns:
        str: JSON-formatted string.

    Raises:
        TypeError: If data is not serializable to JSON.
    """
    try:
        return json.dumps(data, indent=indent, ensure_ascii=False)
    except (TypeError, ValueError) as e:
        msg = f'Error serializing data to JSON: {e}'
        raise TypeError(msg)


def deserialize_json(json_string: str) -> Any:  # noqa: ANN401  # JSON can contain various data types (dict, list, str, etc.)
    """Deserialize a JSON-formatted string into a Python object.

    Args:
        json_string (str): The JSON string to parse.

    Returns:
        Any: Parsed JSON data.

    Raises:
        ValueError: If the JSON string is invalid.
    """
    try:
        return json.loads(json_string)
    except json.JSONDecodeError as e:
        msg = f'Error deserializing JSON string: {e}'
        raise ValueError(msg)
