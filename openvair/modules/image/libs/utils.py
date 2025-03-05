"""Utilities for image file operations.

This module provides helper functions related to image files:

- get_size: Returns the size of a specified file in bytes.
"""

from pathlib import Path


def get_size(file_path: str) -> int:
    """Returns the size of the specified file.

    Args:
        file_path (str): The path of the file to check.

    Returns:
        int: The size of the file in bytes.
    """
    return Path(file_path).stat().st_size
