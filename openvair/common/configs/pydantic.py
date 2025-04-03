"""Pydantic configuration presets for DTO and API models.

This module defines reusable config classes intended for assigning
`model_config` inside Pydantic models. They help enforce consistency
between different types of models (internal DTOs vs API-facing models).

These are not Pydantic models themselves and should not inherit from
`BaseModel`.

Classes:
    - BaseDTOConfig: Strict config used for internal DTOs.
    - ApiModelConfig: Lenient config used for FastAPI request/response models.
"""

from typing import ClassVar

from pydantic import ConfigDict


class DTOConfig:
    """Pydantic config preset for internal DTO models.

    Designed for internal use between service, ORM, and domain layers.

    Behavior:
        - `from_attributes`: Enables ORM-to-Pydantic conversion.
        - `str_strip_whitespace`: Cleans input strings automatically.
        - `extra = "forbid"`: Rejects unexpected fields to avoid silent bugs.
        - `populate_by_name`: Allows aliasing support when using field names.
        - `use_enum_values`: Automatically converts Enums to values.

    Example:
        class MyDTO(BaseModel):
            model_config = BaseDTOConfig.model_config
    """

    model_config: ClassVar[ConfigDict] = ConfigDict(
        from_attributes=True,
        str_strip_whitespace=True,
        str_to_lower=False,
        extra='forbid',
        populate_by_name=True,
        use_enum_values=True,
    )


class APIConfig:
    """Pydantic config preset for public API models.

    Intended for FastAPI request and response schemas.

    Behavior:
        - `from_attributes`: Enables ORM serialization.
        - `extra = "ignore"`: Ignores unknown fields in input (tolerant).
        - `use_enum_values`: Ensures enum fields return readable values.

    Example:
        class CreateRequest(BaseModel):
            model_config = ApiModelConfig.model_config
    """

    model_config: ClassVar[ConfigDict] = ConfigDict(
        from_attributes=True,
        extra='ignore',
        use_enum_values=True,
    )
