"""Serializers for the Template module.

This module defines serializers for converting between Template ORM
models and various DTOs used in different layers of the system.

Classes:
    - TemplateViewSerializer: ORM <-> ViewDTO
    - TemplateCreateSerializer: CreateCommandDTO -> ORM
    - TemplateEditSerializer: Applies MethodData to ORM instance
"""

from openvair.modules.template.adapters.orm import Template as TemplateORM
from openvair.common.serialization.base_serializer import BaseSerializer
from openvair.modules.template.adapters.dto.internal.models import (
    ApiDTO,
    CreateDTO,
    DomainDTO,
)


class ApiSerializer(BaseSerializer[ApiDTO, TemplateORM]):
    """Converts Template ORM <-> ViewDTO."""

    dto_class = ApiDTO
    orm_class = TemplateORM


class DomainSerializer(  # noqa: D101
    BaseSerializer[DomainDTO, TemplateORM]
):
    dto_class = DomainDTO
    orm_class = TemplateORM


class CreateSerializer(BaseSerializer[CreateDTO, TemplateORM]):
    """Converts CreateTemplateDTO -> ORM object for creation."""

    dto_class = CreateDTO
    orm_class = TemplateORM
