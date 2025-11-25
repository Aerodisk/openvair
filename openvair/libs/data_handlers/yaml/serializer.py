"""YAML serialization utilities.

This module provides functions for serializing and deserializing YAML-compatible
data structures.

Functions:
    serialize_yaml: Serializes a Python object into a YAML-formatted string.
    deserialize_yaml: Deserializes a YAML-formatted string into a Python object.
"""

from typing import Any

import yaml


def serialize_yaml(data: Any) -> str:  # noqa: ANN401  # YAML can contain various data types (dict, list, str, etc.)
    """Serialize data into a YAML-formatted string.

    Args:
        data (Any): The data to convert.

    Returns:
        str: YAML-formatted string.

    Raises:
        TypeError: If data is not a valid YAML-compatible type.
    """
    try:
        return yaml.dump(data, sort_keys=False)
    except yaml.YAMLError as e:
        message = f'Error serializing data to YAML: {e}'
        raise TypeError(message)


def deserialize_yaml(yaml_string: str) -> Any:  # noqa: ANN401  # YAML can contain various data types (dict, list, str, etc.)
    """Deserialize a YAML-formatted string into a Python object.

    Args:
        yaml_string (str): The YAML string to parse.

    Returns:
        Any: Parsed YAML data.

    Raises:
        ValueError: If the YAML string contains invalid syntax.
    """
    try:
        return yaml.safe_load(yaml_string) or {}
    except yaml.YAMLError as e:
        message = f'Error deserializing YAML string: {e}'
        raise ValueError(message)
