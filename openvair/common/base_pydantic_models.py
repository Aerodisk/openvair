from pydantic import BaseModel, ConfigDict, model_validator  # noqa: D100


class APIConfigRequestModel(BaseModel):
    """Base schema for incoming API requests related to templates.

    Used as a shared configuration model for request-side schemas
    like template creation, editing, etc.

    Config:
        from_attributes: Enables ORM compatibility.
        extra: Forbids extra fields.
        use_enum_values: Serializes enums as values.
    """

    model_config = ConfigDict(
        from_attributes=True,
        extra='forbid',  # более строгая проверка для входящих данных
        use_enum_values=True,
    )

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

    model_config = ConfigDict(
        from_attributes=True,
        extra='ignore',  # более мягкая — для отдачи наружу
        use_enum_values=True,
    )


class BaseDTOModel(BaseModel):  # noqa: D101
    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
    )
