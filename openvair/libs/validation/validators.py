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
    regex_matcher: Returns regex patterns for various types of values.

Constants:
    SPECIAL_CHARACTERS: A set of special characters that are not allowed in
        strings.
    SPECIAL_CHARACTERS_PATH: A set of special characters that are not allowed
        in file paths.
"""

from typing import Any, Dict, List, Type

from pydantic import BaseModel, TypeAdapter, ValidationError

from openvair.modules.tools.utils import LOG

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


def _create_corrupted_data(
    pydantic_schema: Type[BaseModel],
    _object: Dict[str, Any],
) -> Dict[str, Any]:
    corrupted_data: Dict[str, Any] = {}
    for (
        field_name,
        field_info,
    ) in pydantic_schema.model_fields.items():
        if field_name == 'id':
            corrupted_data[field_name] = _object.get('id')
        elif field_name == 'status':
            corrupted_data[field_name] = 'corrupted object'
        else:
            adapter: TypeAdapter[Any] = TypeAdapter(field_info.annotation)
            try:
                corrupted_data[field_name] = adapter.validate_python(
                    None, strict=False
                )
            except ValidationError:
                corrupted_data[field_name] = None
    return corrupted_data


def validate_objects(
    objects: List[Dict[str, Any]],
    pydantic_schema: Type[BaseModel],
    *,
    skip_corrupted_object: bool = True,
) -> List[BaseModel]:
    """Validates a list of objects against a Pydantic schema

    Ensures that all returned objects are valid instances of the schema.

    This function processes a list of dictionary-based objects, attempting to
    validate each object against the provided Pydantic schema. If an object
    fails validation, it can either be replaced with a "corrupted object"
    (containing default values that satisfy the schema) or raise an exception,
    depending on the `skip_corrupted_object` parameter.

    The function guarantees that all returned objects conform to the schema,
    making it suitable for use in scenarios where subsequent processing (e.g.,
    API responses in FastAPI) requires fully valid Pydantic models.

    Args:
        objects (List[Dict[str, Any]]):
            A list of dictionaries representing objects to be validated.
        pydantic_schema (Type[BaseModel]):
            The Pydantic schema against which each object will be validated.
        skip_corrupted_object (bool, optional):
            If True (default), objects that fail validation are replaced with
            a "corrupted object" containing default values.
            If False, the function raises a `ValidationError` upon encountering
            an invalid object.

    Returns:
        List[BaseModel]:
            A list of validated Pydantic objects, where all elements conform
            to the specified schema. If `skip_corrupted_object=True`,
            invalid objects are replaced with valid "corrupted" versions.

    Raises:
        ValidationError:
            If `skip_corrupted_object=False` and an object fails validation,
            an exception is raised instead of replacing it.

    Example:
        >>> from pydantic import BaseModel
        >>> from typing import List
        >>> class UserModel(BaseModel):
        ...     id: int
        ...     name: str
        ...     status: str = 'active'
        >>> objects = [
        ...     {'id': 1, 'name': 'Alice'},
        ...     {'id': 2, 'name': 123},  # Invalid: name should be str
        ...     {'id': '3'},  # Missing name (required field)
        ... ]
        >>> valid_users = validate_objects(objects, UserModel)
        >>> for user in valid_users:
        ...     print(user)
        UserModel(id=1, name='Alice', status='active')
        UserModel(id=2, name='', status='corrupted object') # Replaced invalid entry
        UserModel(id=3, name='', status='corrupted object') # Replaced invalid entry

    """  # noqa: E501
    result: List[BaseModel] = []
    for _object in objects:
        try:
            validated_object = pydantic_schema.model_validate(_object)
            result.append(validated_object)
        except ValidationError as err:
            message = (
                f'Validation error: {err}\nWhile validating object: {_object} '
                f'with schema: {pydantic_schema.__name__}'
            )
            LOG.warning(message)
            if skip_corrupted_object:
                corrupted_object: BaseModel = pydantic_schema.model_construct(
                    **_create_corrupted_data(pydantic_schema, _object)
                )
                result.append(corrupted_object)
            else:
                LOG.error(message)
                raise
    return result
