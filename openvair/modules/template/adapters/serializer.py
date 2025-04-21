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
    CreateTemplateDTO,
    ApiTemplateViewDTO,
    DomainTemplateManagerDTO,
)


class TemplateViewSerializer(BaseSerializer[ApiTemplateViewDTO, TemplateORM]):
    """Converts Template ORM <-> ViewDTO."""

    dto_class = ApiTemplateViewDTO
    orm_class = TemplateORM


class TemplateDomainSerializer(  # noqa: D101
    BaseSerializer[DomainTemplateManagerDTO, TemplateORM]
):
    dto_class = DomainTemplateManagerDTO
    orm_class = TemplateORM


class TemplateCreateSerializer(BaseSerializer[CreateTemplateDTO, TemplateORM]):
    """Converts CreateTemplateDTO -> ORM object for creation."""

    dto_class = CreateTemplateDTO
    orm_class = TemplateORM
