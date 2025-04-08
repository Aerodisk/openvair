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

api_request_config = ConfigDict(
    from_attributes=True,
    extra='forbid',  # более строгая проверка для входящих данных
    use_enum_values=True,
)

api_response_config = ConfigDict(
    from_attributes=True,
    extra='ignore',  # более мягкая — для отдачи наружу
    use_enum_values=True,
)

dto_config = ConfigDict(
    from_attributes=True,
    extra='forbid',
    populate_by_name=True,
    use_enum_values=True,
    str_strip_whitespace=True,
)

lenient_dto_config = ConfigDict(
    from_attributes=True,
    extra='ignore',
    populate_by_name=True,
    use_enum_values=True,
    str_strip_whitespace=True,
)
