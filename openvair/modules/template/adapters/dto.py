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


class BaseTemplateDTO(BaseModel):
    """Base DTO for the template entity.

    Contains core fields used across Template-related DTOs.

    Attributes:
        name (str): Name of the template.
        description (Optional[str]): Description of the template.
        path (Path): Filesystem path to the template.
        storage_id (UUID): ID of the associated storage backend.
        is_backing (bool): Whether it's a backing image.

    Example:
        >>> BaseTemplateDTO(
        ...     name='base-template',
        ...     path=Path('/mnt/template.qcow2'),
        ...     storage_id=UUID('...'),
        ...     is_backing=True,
        ... )
    """
    name: str
    description: Optional[str]
    path: Path
    storage_id: UUID
    is_backing: bool
    model_config: ClassVar[ConfigDict] = ConfigDict(**DTOConfig.model_config)

class TemplateDTO(BaseTemplateDTO):
    """DTO representing a complete template record.

    Includes metadata fields such as ID and creation time.

    Attributes:
        id (UUID): Unique ID of the template.
        created_at (datetime): Timestamp of creation.
    """
    id: UUID
    created_at: datetime


class TemplateCreateDTO(BaseTemplateDTO):
    """DTO used for creating a new template.

    Attributes:
        base_volume_id (UUID): ID of the base volume to clone.
    """
    base_volume_id: UUID


class TemplateEditDTO(BaseTemplateDTO):
    """DTO used for partial updates to a template.

    Attributes:
        description (Optional[str]): New description, if applicable.
    """

    description: Optional[str] = None


class TemplateDataDTO(BaseTemplateDTO):
    """DTO used for referencing a template by name.

    Includes only the name field. Useful for lightweight links.

    Attributes:
        name (str): Name of the template.
    """
    name: str
