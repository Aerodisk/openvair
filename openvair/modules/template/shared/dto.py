"""DTO models for the Template module.

This module defines Pydantic-based DTOs used to transfer
and validate data between the ORM and external layers.

Classes:
    - TemplateDTO: DTO for Template ORM model.
    - TemplateCreateDTO: DTO for creating templates.
    - TemplateEditDTO: DTO for editing templates.
    - TemplateDataDTO: Lightweight DTO with only name field.

Example:
    orm = Template(...)
    dto = TemplateSerializer.to_dto(orm)
"""

from uuid import UUID
from typing import ClassVar, Optional
from pathlib import Path
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from openvair.common.configs.pydantic import DTOConfig


class TemplateDTO(BaseModel):
    """DTO representing a template object.

    Attributes:
        id (UUID): Template ID.
        created_at (datetime): Creation timestamp.

    Example:
        TemplateDTO(
            id=UUID("..."),
            name="base-template",
            path=Path("/path.qcow2"),
            storage_id=UUID("..."),
            created_at=datetime.utcnow(),
            is_backing=True
        )
    """

    id: UUID
    name: str
    description: Optional[str]
    path: Path
    storage_id: UUID
    is_backing: bool
    created_at: datetime
    model_config: ClassVar[ConfigDict] = ConfigDict(**DTOConfig.model_config)


class TemplateCreateDTO(TemplateDTO):
    """DTO for creating a new template.

    Attributes:
        base_volume_id (UUID): ID of the base volume to use.
    """

    base_volume_id: UUID


class TemplateEditDTO(TemplateDTO):
    """DTO for editing a template.

    All fields are optional to support partial updates.
    """

    description: Optional[str] = None


class TemplateDataDTO(TemplateDTO):
    """DTO containing only name of the template (e.g., for referencing).

    Example:
        TemplateDataDTO(name="template-name")
    """

    name: str
