"""Template serializer mapping between ORM and DTO.

This serializer converts between Template ORM model and TemplateDTO.
It is auto-registered in SerializerHub.

Classes:
    - TemplateSerializer: Converts Template <-> TemplateDTO
"""

from openvair.modules.template.adapters.dto import BaseTemplateDTO
from openvair.modules.template.adapters.orm import Template as TemplateORM
from openvair.common.serialization.base_serializer import BaseSerializer


class TemplateSerializer(BaseSerializer[BaseTemplateDTO, TemplateORM]):
    """Converts Template ORM to DTO and back."""

    name = 'template'
    dto_class = BaseTemplateDTO
    orm_class = TemplateORM
