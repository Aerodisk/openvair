"""Validators for various data types.

This module provides validation functions for UUIDs, paths, and special
characters. These functions can be used to ensure that input data meets
specific criteria.

Functions:
    uuid_validate: Validates a UUID string.
    path_validate: Validates a file path string.
    special_characters_validate: Ensures a string does not contain special
        characters.
    special_characters_path_validate: Ensures a file path does not contain
        special characters.

Constants:
    SPECIAL_CHARACTERS: A set of special characters that are not allowed in
        strings.
    SPECIAL_CHARACTERS_PATH: A set of special characters that are not allowed
        in file paths.
"""

from uuid import UUID

SPECIAL_CHARACTERS = {
    '!',
    '@',
    '#',
    '$',
    '%',
    '^',
    '&',
    '*',
    '(',
    ')',
    '+',
    '?',
    '=',
    '<',
    '>',
    '/',
    '~',
    '{',
    '}',
    '|',
    "''",
    ':',
    ';',
    "'",
    '"',
}
SPECIAL_CHARACTERS_PATH = {
    '!',
    '@',
    '#',
    '$',
    '%',
    '^',
    '&',
    '*',
    '(',
    ')',
    '+',
    '?',
    '=',
    '<',
    '>',
    '~',
    '{',
    '}',
    '|',
    "''",
    ':',
    ';',
    "'",
    '"',
}


def uuid_validate(value: str) -> str:
    """Validates a UUID string.

    Args:
        value (str): The UUID string to validate.

    Returns:
        str: The validated UUID string.

    Raises:
        ValueError: If the value is not a valid UUID.
    """
    try:
        UUID(value, version=4)
    except ValueError:
        msg = 'Not a valid UUID'
        raise ValueError(msg)
    return str(value)


def special_characters_validate(value: str) -> str:
    """Ensures a string does not contain special characters.

    Args:
        value (str): The string to validate.

    Returns:
        str: The validated string.

    Raises:
        ValueError: If the string contains special characters.
    """
    if any(c in SPECIAL_CHARACTERS for c in value):
        msg = 'There should be no special characters in the string.'
        raise ValueError(msg)
    return value


def special_characters_path_validate(value: str) -> str:
    """Ensures a file path does not contain special characters.

    Args:
        value (str): The file path to validate.

    Returns:
        str: The validated file path.

    Raises:
        ValueError: If the file path contains special characters.
    """
    if any(c in SPECIAL_CHARACTERS_PATH for c in value):
        msg = 'There should be no special characters in the path.'
        raise ValueError(msg)
    return value
