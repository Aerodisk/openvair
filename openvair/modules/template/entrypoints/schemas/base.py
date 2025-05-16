"""Base Pydantic schemas for template API models.

Defines shared request and response configuration models used across
multiple template-related API schemas.
"""

from pydantic import BaseModel, model_validator

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

    @model_validator(mode='after')
    def _at_least_one_field_must_be_present(self) -> 'APIConfigRequestModel':
        """Ensure that at least one field is not None.

        Raises:
            ValueError: If all fields are None.
        """
        if all(getattr(self, field) is None for field in self.__annotations__):
            message = 'At least one field must be provided'
            raise ValueError(message)
        return self


class APIConfigResponseModel(BaseModel):
    """Base schema for outgoing API responses related to templates.

    Used as a shared configuration model for response-side schemas.

    Config:
        from_attributes: Enables ORM compatibility.
        extra: Allows extra fields.
        use_enum_values: Serializes enums as values.
    """

    model_config = api_response_config
