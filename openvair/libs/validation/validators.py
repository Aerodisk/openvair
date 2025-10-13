"""Validators for various data types.

This module provides validation functions for different types of input data,
such as checking for special characters and validating objects against
Pydantic schemas. It ensures input meets specific criteria before further
processing.

Classes:
    Validator: A utility class for performing various validation tasks.
"""

from typing import Any, TypeVar, ClassVar, cast
from collections.abc import Sequence

from pydantic import (
    BaseModel,
    TypeAdapter,
    ValidationError,
)

from openvair.libs.log import get_logger

LOG = get_logger(__name__)
T = TypeVar('T', bound=BaseModel)


class Validator:
    """A collection of validation methods for different types of input data.

    This class provides methods for validating the presence of special
    characters in a string and ensuring objects conform to a given
    Pydantic schema.

    Attributes:
        SPECIAL_CHARACTERS (ClassVar[Set]): A set of special characters that
            should not appear in validated input.
    """

    SPECIAL_CHARACTERS: ClassVar = set('!@#$%^&*()+?=<>/~{}|\'":;')

    @staticmethod
    def special_characters_validate(
        value: str,
        *,
        allow_slash: bool = False,
    ) -> str:
        """Check if the input string contains any special characters.

        Scans the input and raises `ValueError` if any forbidden characters are
        found. Optionally allows the slash ('/') character, which is useful for
        validating path-like strings.

        Args:
            value (str): The string to be validated.
            allow_slash (bool): If True, the slash '/' is excluded from the
                forbidden set and will be allowed.

        Returns:
            str: The original string if no forbidden characters are present.

        Raises:
            ValueError: If the input contains any forbidden characters.
        """
        forbidden_chars = Validator.SPECIAL_CHARACTERS
        if allow_slash:
            forbidden_chars = forbidden_chars - {'/'}
        if any(c in forbidden_chars for c in value):
            msg = 'There should be no special characters.'
            raise ValueError(msg)
        return value

    @classmethod
    def validate_objects(
        cls,
        objects: Sequence[dict[str, Any]],
        pydantic_schema: type[T],
        *,
        skip_corrupted_object: bool = True,
    ) -> list[T]:
        """Validate a sequence of dicts against a Pydantic model and return `List[T]`.

        This method attempts to validate each dictionary in `objects` using the
        provided Pydantic model class `pydantic_schema` (a subclass of `BaseModel`).
        On successful validation, an instance of `T` is appended to the result.

        If validation fails for an item:
            - When `skip_corrupted_object=True` (default), the invalid item is
              replaced with a generated "corrupted object" that still conforms to
              the target model `T` (see `_create_corrupted_data`).
            - When `skip_corrupted_object=False`, a `ValidationError` is raised
              immediately for the offending item.

        This guarantees that the returned list contains only instances of `T`,
        making the result convenient and safe for further processing (e.g., for
        serialization in API responses).

        Type parameters:
            T (BaseModel): A concrete Pydantic model subclass.

        Args:
            objects (Sequence[Dict[str, Any]]): A sequence of raw dictionaries to
                validate against the given schema.
            pydantic_schema (Type[T]): The Pydantic model class used for validation.
            skip_corrupted_object (bool, optional): If True, replaces invalid items
                with a conforming "corrupted object"; if False, raises on first
                invalid item. Defaults to True.

        Returns:
            List[T]: A list of validated instances of `pydantic_schema`.

        Raises:
            ValidationError: If `skip_corrupted_object` is False and an invalid
                object is encountered.

        Example:
            >>> from pydantic import BaseModel
            >>> class UserModel(BaseModel):
            ...     id: int
            ...     name: str
            ...     status: str = 'active'
            >>> objects = [
            ...     {'id': 1, 'name': 'Alice'},
            ...     {'id': 2, 'name': 123},  # invalid: name should be str
            ...     {'id': '3'},  # invalid: missing name
            ... ]
            >>> valid_users = Validator.validate_objects(objects, UserModel)
            >>> for user in valid_users:
            ...     print(user)
            UserModel(id=1, name='Alice', status='active')
            UserModel(id=2, name='', status='corrupted object')
            UserModel(id=3, name='', status='corrupted object')
        """  # noqa: E501
        result: list[T] = []
        for _object in objects:
            try:
                validated_object: T = pydantic_schema.model_validate(_object)
                result.append(validated_object)
            except ValidationError as err:
                message = (
                    f'Validation error: {err}\nWhile validating object: '
                    f'{_object} with schema: {pydantic_schema.__name__}'
                )
                LOG.warning(message)
                if skip_corrupted_object:
                    corrupted_object = cast(
                        'T',
                        pydantic_schema.model_construct(
                            **cls._create_corrupted_data(
                                pydantic_schema, _object
                            )
                        ),
                    )
                    result.append(corrupted_object)
                else:
                    LOG.error(message)
                    raise
        return result

    @classmethod
    def _create_corrupted_data(
        cls,
        pydantic_schema: type[T],
        _object: dict[str, Any],
    ) -> dict[str, Any]:
        """Generate a conforming 'corrupted object' payload for the given schema

        Builds a dictionary that satisfies the field requirements of the target
        Pydantic model `pydantic_schema`, using the following rules:

            - If the field name is `'id'`, reuse the value from the original
              object (if present).
            - If the field name is `'status'`, set it to `'corrupted object'`.
            - For all other fields, attempt to validate `None` using a
                field-level `TypeAdapter`. If it still fails, fall back to
                `None`.

        This payload is then used with `model_construct(**payload)` to create a
        valid instance of `T` without running full validation, ensuring the
        returned object is structurally compatible with the schema.

        Args:
            pydantic_schema (Type[T]): The Pydantic model class used to shape
                the corrupted payload.
            _object (Dict[str, Any]): The original invalid item that failed
                validation.

        Returns:
            Dict[str, Any]: A dict payload that conforms to `pydantic_schema`
            and can be passed to `model_construct(**payload)`.
        """
        corrupted_data: dict[str, Any] = {}
        for field_name, field_info in pydantic_schema.model_fields.items():
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
