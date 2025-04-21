"""Registry system for managing DTO-to-ORM serializers.

This module provides a central registry (`SerializerHub`) to map and
retrieve serializers based on DTO type, ORM class, or string name.
It enables decoupled and scalable serialization logic.

Typical usage involves:
    - Auto-registration via `BaseSerializer`
    - Manual lookup of serializer class by DTO or ORM type

Classes:
    - SerializerHub: Central registry for mapping serializers.
"""

from typing import Any, Dict, Type, TypeVar, ClassVar

from pydantic import BaseModel
from sqlalchemy.orm import DeclarativeBase

DTO = TypeVar('DTO', bound=BaseModel)
ORM = TypeVar('ORM', bound=DeclarativeBase)


class SerializerHub:
    """Registry for linking DTOs, ORM models, and serializers.

    Allows retrieving serializers by name, DTO class, or ORM class.
    Enables decoupled lookup in generic components.
    """

    _by_name: ClassVar[Dict[str, Type]] = {}
    _by_dto: ClassVar[Dict[Any, Type]] = {}
    _by_orm: ClassVar[Dict[Any, Type]] = {}

    @classmethod
    def register(
        cls,
        name: str,
        serializer: Type,
        dto_class: Type[DTO],
        orm_class: Type[ORM],
    ) -> None:
        """Register a new serializer in the hub.

        Args:
            name (str): Unique name of the serializer.
            serializer (Type): Serializer class.
            dto_class (Type[DTO]): DTO class.
            orm_class (Type[ORM]): ORM class.

        Example:
            SerializerHub.register(
                name="template",
                serializer=TemplateSerializer,
                dto_class=TemplateDTO,
                orm_class=TemplateORM,
            )
        """
        cls._by_name[name] = serializer
        cls._by_dto[dto_class] = serializer
        cls._by_orm[orm_class] = serializer

    @classmethod
    def get(cls, name: str) -> Type:
        """Retrieve a serializer by its name.

        Args:
            name (str): The serializer's name.

        Returns:
            Type: Serializer class.
        """
        return cls._by_name[name]

    @classmethod
    def get_by_dto(cls, dto_class: Type[DTO]) -> Type:
        """Retrieve a serializer by DTO class.

        Args:
            dto_class (Type[DTO]): DTO class.

        Returns:
            Type: Serializer class.
        """
        return cls._by_dto[dto_class]

    @classmethod
    def get_by_orm(cls, orm_class: Type[ORM]) -> Type:
        """Retrieve a serializer by ORM class.

        Args:
            orm_class (Type[ORM]): ORM class.

        Returns:
            Type: Serializer class.
        """
        return cls._by_orm[orm_class]
