"""Base class for implementing custom ORM <-> DTO serializers.

This module defines `BaseSerializer` for converting between ORM objects
and DTOs. It supports nested serializers and automatic registration in
`SerializerHub`. Designed to be subclassed per entity.

Example:
    class TemplateSerializer(BaseSerializer[TemplateDTO, TemplateORM]):
        dto_class = TemplateDTO
        orm_class = TemplateORM

    orm = TemplateSerializer.to_orm(template_dto)
    dto = TemplateSerializer.to_dto(template_orm)

Classes:
    - BaseSerializer: Generic base class for all serializers.

Dependencies:
    - Registers itself in SerializerHub upon subclassing.
"""

from typing import Any, Dict, Type, Generic, TypeVar, ClassVar, cast

from pydantic import BaseModel
from sqlalchemy import inspect
from sqlalchemy.orm import DeclarativeBase

DTO = TypeVar('DTO', bound=BaseModel)
ORM = TypeVar('ORM', bound=DeclarativeBase)


class BaseSerializer(Generic[DTO, ORM]):
    """Base class for converting ORM <-> DTO objects.

    Designed to be subclassed with entity-specific logic. Supports
    nested serializers for related objects.

    Attributes:
        dto_class (Type[DTO]): DTO model class.
        orm_class (Type[ORM]): ORM SQLAlchemy model class.
        nested_serializers (Dict[str, Type["BaseSerializer"]]):
            Field-to-serializer mapping.
    """

    dto_class: Type[DTO]
    orm_class: Type[ORM]
    nested_serializers: ClassVar[Dict[str, Type['BaseSerializer']]] = {}

    @classmethod
    def to_dto(cls, orm_obj: ORM) -> DTO:
        """Convert ORM model to DTO object.

        Args:
            orm_obj (ORM): The ORM instance.

        Returns:
            DTO: Populated DTO model.

        Example:
            dto = TemplateSerializer.to_dto(orm_obj)
        """
        data: Dict[str, Any] = {}
        for field in cls.dto_class.model_fields:
            value = getattr(orm_obj, field, None)
            if field in cls.nested_serializers and isinstance(value, list):
                nested = cls.nested_serializers[field]
                data[field] = [nested.to_dto(item) for item in value]
            else:
                data[field] = value
        return cast(DTO, cls.dto_class(**data))

    @classmethod
    def to_orm(cls, dto_obj: DTO) -> ORM:
        """Convert DTO object to ORM model.

        Args:
            dto_obj (DTO): The DTO instance.

        Returns:
            ORM: New ORM object.

        Example:
            orm = TemplateSerializer.to_orm(dto)
        """
        dto_data = dto_obj.model_dump()
        inspected = inspect(cls.orm_class)
        orm_fields = {col.key for col in inspected.mapper.column_attrs}

        nested_data: Dict[str, Any] = {}
        for field, value in dto_data.items():
            if field in cls.nested_serializers and isinstance(value, list):
                nested = cls.nested_serializers[field]
                nested_data[field] = [nested.to_orm(item) for item in value]

        filtered = {k: v for k, v in dto_data.items() if k in orm_fields}
        orm = cls.orm_class(**filtered)

        for key, val in nested_data.items():
            setattr(orm, key, val)

        return cast(ORM, orm)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ORM:
        """Convert raw dictionary to ORM model via DTO.

        Args:
            data (Dict[str, Any]): Input data as dictionary.

        Returns:
            ORM: ORM object constructed from the data.
        """
        dto = cls.dto_class.model_validate(data)
        return cls.to_orm(dto)

    @classmethod
    def to_dict(cls, orm_obj: ORM) -> Dict[str, Any]:
        """Convert ORM object to dictionary via DTO.

        Args:
            orm_obj (ORM): ORM model instance.

        Returns:
            Dict[str, Any]: Dictionary representation of the object.
        """
        dto = cls.to_dto(orm_obj)
        return dto.model_dump(mode='json')

    @classmethod
    def update_orm(cls, orm_obj: ORM, dto_obj: DTO) -> ORM:
        """Update existing ORM object from DTO.

        Args:
            orm_obj (ORM): Existing ORM instance to update.
            dto_obj (DTO): DTO with new values.

        Returns:
            ORM: Updated ORM object (same instance).
        """
        dto_data = dto_obj.model_dump()
        inspected = inspect(cls.orm_class)
        orm_fields = {col.key for col in inspected.mapper.column_attrs}

        for field, value in dto_data.items():
            if field in orm_fields:
                setattr(orm_obj, field, value)

        return orm_obj

    @classmethod
    def update_orm_from_dict(cls, orm_obj: ORM, data: Dict[str, Any]) -> ORM:
        """Update an existing ORM object from a dictionary via DTO validation.

        This method converts the input dictionary into a DTO instance and
        applies its values to the given ORM object. Only ORM-declared column
        fields are updated. Relationships or nested fields are not handled
        unless explicitly supported by the DTO.

        Args:
            orm_obj (ORM): The existing ORM instance to be updated.
            data (Dict[str, Any]): A dictionary representing new field values.

        Returns:
            ORM: The updated ORM instance with modified fields.

        Example:
            updated = TemplateDomainSerializer.update_orm_from_dict(
                orm_template, incoming_data
            )
        """
        dto = cls.dto_class.model_validate(data)
        return cls.update_orm(orm_obj, dto)
