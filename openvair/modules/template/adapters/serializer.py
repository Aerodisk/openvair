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
    ApiTemplateModel,
    CreateTemplateModel,
    DomainTemplateModel,
)


class ApiSerializer(BaseSerializer[ApiTemplateModel, TemplateORM]):
    """Converts Template ORM <-> ViewDTO."""

    dto_class = ApiTemplateModel
    orm_class = TemplateORM


class DomainSerializer(  # noqa: D101
    BaseSerializer[DomainTemplateModel, TemplateORM]
):
    dto_class = DomainTemplateModel
    orm_class = TemplateORM


class CreateSerializer(BaseSerializer[CreateTemplateModel, TemplateORM]):
    """Converts CreateTemplateDTO -> ORM object for creation."""

    dto_class = CreateTemplateModel
    orm_class = TemplateORM
