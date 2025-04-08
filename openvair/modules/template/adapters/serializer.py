"""Template serializer mapping between ORM and DTO.

This serializer converts between Template ORM model and TemplateDTO.
It is auto-registered in SerializerHub.

Classes:
    - TemplateSerializer: Converts Template <-> TemplateDTO
"""

from openvair.modules.template.adapters.orm import Template as TemplateORM
from openvair.common.serialization.base_serializer import BaseSerializer
from openvair.modules.template.adapters.dto.templates import DTOTemplate


class TemplateSerializer(BaseSerializer[DTOTemplate, TemplateORM]):
    """Converts Template ORM to DTO and back."""

    name = 'template'
    dto_class = DTOTemplate
    orm_class = TemplateORM
