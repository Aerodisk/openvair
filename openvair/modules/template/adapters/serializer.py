"""Serializers for the Template module.

Provides conversion logic between ORM models and DTOs used at API and domain
layers.

Classes:
    - ApiSerializer: ORM <-> API DTO
    - DomainSerializer: ORM <-> Domain DTO
    - CreateSerializer: Create DTO -> ORM
"""

from openvair.modules.template.adapters.orm import Template as TemplateORM
from openvair.common.serialization.base_serializer import BaseSerializer
from openvair.modules.template.adapters.dto.internal.models import (
    ApiTemplateModelDTO,
    CreateTemplateModelDTO,
    DomainTemplateModelDTO,
)


class ApiSerializer(BaseSerializer[ApiTemplateModelDTO, TemplateORM]):
    """Serializer for converting between Template ORM and API DTO."""

    dto_class = ApiTemplateModelDTO
    orm_class = TemplateORM


class DomainSerializer(BaseSerializer[DomainTemplateModelDTO, TemplateORM]):
    """Serializer for converting between Template ORM and Domain DTO."""

    dto_class = DomainTemplateModelDTO
    orm_class = TemplateORM


class CreateSerializer(BaseSerializer[CreateTemplateModelDTO, TemplateORM]):
    """Serializer for converting creation DTO into ORM Template model."""

    dto_class = CreateTemplateModelDTO
    orm_class = TemplateORM
