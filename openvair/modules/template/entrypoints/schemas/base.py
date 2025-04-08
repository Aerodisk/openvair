"""Base Pydantic schemas for template API models.

Defines shared request and response configuration models used across
multiple template-related API schemas.
"""

from typing import ClassVar

from pydantic import BaseModel, ConfigDict


class APIConfigRequestModel(BaseModel):
    """Base schema for incoming API requests related to templates.

    Used as a shared configuration model for request-side schemas
    like template creation, editing, etc.

    Config:
        from_attributes: Enables ORM compatibility.
        extra: Forbids extra fields.
        use_enum_values: Serializes enums as values.
    """

    model_config: ClassVar[ConfigDict] = ConfigDict(
        from_attributes=True,
        extra='forbid',
        use_enum_values=True,
    )


class APIConfigResponseModel(BaseModel):
    """Base schema for outgoing API responses related to templates.

    Used as a shared configuration model for response-side schemas.

    Config:
        from_attributes: Enables ORM compatibility.
        extra: Allows extra fields.
        use_enum_values: Serializes enums as values.
    """

    model_config: ClassVar[ConfigDict] = ConfigDict(
        from_attributes=True,
        extra='ignore',
        use_enum_values=True,
    )
