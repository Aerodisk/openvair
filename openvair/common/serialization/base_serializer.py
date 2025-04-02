"""Base class for implementing custom ORM <-> DTO serializers.

This module defines `BaseSerializer` for converting between ORM objects
and DTOs. It supports nested serializers and automatic registration in
`SerializerHub`. Designed to be subclassed per entity.

Example:
    class TemplateSerializer(BaseSerializer[TemplateDTO, TemplateORM]):
        name = "template"
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
from sqlalchemy.orm import DeclarativeBase

from openvair.common.serialization.serializer_hub import SerializerHub

DTO = TypeVar('DTO', bound=BaseModel)
ORM = TypeVar('ORM', bound=DeclarativeBase)


class BaseSerializer(Generic[DTO, ORM]):
    """Base class for converting ORM <-> DTO objects.

    Designed to be subclassed with entity-specific logic. Supports
    nested serializers for related objects.

    Attributes:
        dto_class (Type[DTO]): DTO model class.
        orm_class (Type[ORM]): ORM SQLAlchemy model class.
        name (str): Unique name for registration.
        nested_serializers (Dict[str, Type["BaseSerializer"]]):
            Field-to-serializer mapping.
    """

    dto_class: Type[DTO]
    orm_class: Type[ORM]
    name: str
    nested_serializers: ClassVar[Dict[str, Type['BaseSerializer']]] = {}

    def __init_subclass__(cls) -> None:
        """Automatically registers the serializer in SerializerHub."""
        if (
            hasattr(cls, 'name')
            and hasattr(cls, 'dto_class')
            and hasattr(cls, 'orm_class')
        ):
            SerializerHub.register(
                name=cls.name,
                serializer=cls,
                dto_class=cls.dto_class,
                orm_class=cls.orm_class,
            )

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
        fields = cls.orm_class.__table__.columns.keys()
        dto_data = dto_obj.model_dump()
        nested_data: Dict[str, Any] = {}
        for field, value in dto_data.items():
            if field in cls.nested_serializers and isinstance(value, list):
                nested = cls.nested_serializers[field]
                nested_data[field] = [nested.to_orm(item) for item in value]
        filtered = {k: v for k, v in dto_data.items() if k in fields}
        orm = cls.orm_class(**filtered)
        for key, val in nested_data.items():
            setattr(orm, key, val)
        return cast(ORM, orm)
