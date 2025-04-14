"""Serializers for the Template module.

This module defines serializers for converting between Template ORM
models and various DTOs used in different layers of the system.

Classes:
    - TemplateViewSerializer: ORM <-> ViewDTO
    - TemplateCreateSerializer: CreateCommandDTO.ManagerData -> ORM
    - TemplateEditSerializer: Applies MethodData to ORM instance
"""

from openvair.modules.template.adapters.orm import Template as TemplateORM
from openvair.common.serialization.base_serializer import BaseSerializer
from openvair.modules.template.adapters.dto.internal.models import (
    ApiTemplateViewDTO,
)
from openvair.modules.template.adapters.dto.internal.commands import (
    EditTemplateCommandDTO,
    CreateTemplateServiceCommandDTO,
)


class TemplateViewSerializer(BaseSerializer[ApiTemplateViewDTO, TemplateORM]):
    """Converts Template ORM <-> ViewDTO."""

    dto_class = ApiTemplateViewDTO
    orm_class = TemplateORM


class TemplateCreateSerializer(
    BaseSerializer[CreateTemplateServiceCommandDTO, TemplateORM]
):
    """Converts CreateTemplateDTO.ManagerData -> ORM object for creation."""

    dto_class = CreateTemplateServiceCommandDTO
    orm_class = TemplateORM


class TemplateEditSerializer:
    """Applies changes from EditTemplateDTO.MethodData to an existing ORM object."""  # noqa: E501

    @staticmethod
    def apply_changes(
        orm_obj: TemplateORM,
        dto: EditTemplateCommandDTO.MethodData,
    ) -> None:
        """Apply fields from DTO to ORM instance.

        Args:
            orm_obj (TemplateORM): Existing ORM object to update.
            dto (EditTemplateDTO.MethodData): DTO with new field values.
        """
        update_fields = dto.model_dump(exclude_unset=True)
        for field, value in update_fields.items():
            setattr(orm_obj, field, value)
