"""Defines a base DTO model used across the application.

This module provides a shared Pydantic base model (`BaseDTO`) with
common config options for all DTOs used in service and domain layers.
It enforces consistent validation, attribute mapping from ORM,
and serialization rules.

Use this as a superclass when creating new DTOs.

Example:
    class MyDTO(BaseDTO):
        id: UUID
        name: str

Classes:
    - BaseDTO: Base class for all Data Transfer Objects (DTOs).
"""

from pydantic import BaseModel


class BaseDTO(BaseModel):
    """Base class for Data Transfer Objects with shared config.

    Applies global serialization and validation settings such as
    stripping whitespace, forbidding extra fields, and supporting
    attribute population from ORM models.
    """

    model_config = {
        'from_attributes': True,
        'str_strip_whitespace': True,
        'str_to_lower': False,
        'extra': 'forbid',
        'populate_by_name': True,
        'use_enum_values': True,
    }
