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

from pydantic import ConfigDict

dto_config = ConfigDict(
    from_attributes=True,
    populate_by_name=True,
    use_enum_values=True,
    str_strip_whitespace=True,
)

lenient_dto_config = ConfigDict(
    from_attributes=True,
    use_enum_values=True,
)
