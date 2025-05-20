"""Base Pydantic schemas for template API models.

Defines shared request and response configuration models used across
multiple template-related API schemas.
"""

from pydantic import BaseModel

from openvair.common.configs.pydantic_config import (
    api_request_config,
    api_response_config,
)


class APIConfigRequestModel(BaseModel):
    """Base schema for incoming API requests related to templates.

    Used as a shared configuration model for request-side schemas
    like template creation, editing, etc.

    Config:
        from_attributes: Enables ORM compatibility.
        extra: Forbids extra fields.
        use_enum_values: Serializes enums as values.
    """

    model_config = api_request_config


class APIConfigResponseModel(BaseModel):
    """Base schema for outgoing API responses related to templates.

    Used as a shared configuration model for response-side schemas.

    Config:
        from_attributes: Enables ORM compatibility.
        extra: Allows extra fields.
        use_enum_values: Serializes enums as values.
    """

    model_config = api_response_config
