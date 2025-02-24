"""Validators for various data types.

This module provides validation functions for different types of input data,
such as checking for special characters and validating objects against
Pydantic schemas. It ensures input meets specific criteria before further
processing.

Classes:
    Validator: A utility class for performing various validation tasks.
"""

from typing import Any, Dict, List, Type, ClassVar

from pydantic import (
    BaseModel,
    TypeAdapter,
    ValidationError,
)

from openvair.modules.tools.utils import LOG


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
    def special_characters_validate(value: str) -> str:
        """Check if the input string contains any special characters.

        This function scans the input string and raises a `ValueError` if any
        of the predefined special characters are found.

        Args:
            value (str): The string to be validated.

        Returns:
            str: The original string if no special characters are present.

        Raises:
            ValueError: If the input contains any special characters.
        """
        if any(c in Validator.SPECIAL_CHARACTERS for c in value):
            msg = 'There should be no special characters.'
            raise ValueError(msg)
        return value

    @classmethod
    def validate_objects(
        cls,
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
                    f'Validation error: {err}\nWhile validating object: '
                    f'{_object} '
                    f'with schema: {pydantic_schema.__name__}'
                )
                LOG.warning(message)
                if skip_corrupted_object:
                    corrupted_object: BaseModel = (
                        pydantic_schema.model_construct(
                            **cls._create_corrupted_data(
                                pydantic_schema, _object
                            )
                        )
                    )
                    result.append(corrupted_object)
                else:
                    LOG.error(message)
                    raise
        return result

    @classmethod
    def _create_corrupted_data(
        cls,
        pydantic_schema: Type[BaseModel],
        _object: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate a "corrupted object" with valid default values.

        This method constructs a dictionary with default values that conform
        to the given Pydantic schema. The "corrupted object" replaces invalid
        entries in the validation process.

        Args:
            pydantic_schema (Type[BaseModel]): The schema to use for generating
                valid defaults.
            _object (Dict[str, Any]): The original object that failed
                validation.

        Returns:
            Dict[str, Any]: A dictionary with valid default values that match
            the schema.
        """
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
