"""Pydantic schemas for the template module.

This module defines data validation and serialization models used in the
template API and service layer.

Schemas:
    - APITemplateBase: Common base schema with API config.
    - CreateTemplate: Schema for creating a new template.
    - Template: Full representation of a template, including metadata.
    - EditTemplate: Schema for updating template name or description.
    - CreateVolumeFromTemplate: Input for creating a volume from a template.
    - Volume: Volume created from a template.
    - TemplateData: Minimal template name representation.

Dependencies:
    - Used in FastAPI endpoints and integrated with shared base schemas.
"""

from uuid import UUID
from typing import ClassVar, Optional
from pathlib import Path
from datetime import datetime

from pydantic import Field, BaseModel, ConfigDict

from openvair.common.configs.pydantic import APIConfig


class Template(BaseModel):
    """Schema representing a template returned from the API.

    Extends APITemplateBase with additional metadata fields.

    Attributes:
        id (UUID): Unique identifier of the template.
        created_at (datetime): Timestamp of when the template was created.

    Example:
        >>> Template(
        ...     id=UUID('...'),
        ...     name='ubuntu-template',
        ...     path=Path('/mnt/ubuntu.qcow2'),
        ...     storage_id=UUID('...'),
        ...     is_backing=True,
        ...     created_at=datetime.utcnow(),
        ... )
    """

    id: UUID
    name: str
    description: Optional[str]
    path: Path
    storage_id: UUID
    is_backing: bool
    created_at: datetime

    model_config: ClassVar[ConfigDict] = ConfigDict(**APIConfig.model_config)


class CreateTemplate(Template):
    """Schema for creating a new template.

    Inherits common fields from APITemplateBase and adds the field
    for selecting a base volume from which to create the template.

    Attributes:
        base_volume_id (UUID): ID of the base volume to use for the template.

    Example:
        >>> CreateTemplate(
        ...     name='ubuntu-template',
        ...     path=Path('/mnt/ubuntu.qcow2'),
        ...     storage_id=UUID('...'),
        ...     is_backing=True,
        ...     base_volume_id=UUID('...'),
        ... )
    """

    base_volume_id: UUID


class EditTemplate(Template):
    """Schema for updating a template.

    Attributes:
        name (Optional[str]): New name of the template.
        description (Optional[str]): New description of the template.
    """

    name: str = Field(None, min_length=1, max_length=40)
    description: Optional[str] = Field(None, max_length=255)


class CreateVolumeFromTemplate(Template):
    """Schema for creating a volume from a template.

    Attributes:
        name (str): Name of the new volume.
        size (int): Size of the volume in bytes.
    """

    name: str = Field(
        ..., min_length=1, max_length=40, description='Имя нового volume'
    )
    size: int = Field(..., gt=0, description='Размер volume в байтах')


class Volume(BaseModel):
    """Schema representing a volume created from a template.

    Attributes:
        id (UUID): Volume identifier.
        name (str): Name of the volume.
        size (int): Volume size in bytes.
        status (str): Current status of the volume.
        path (str): Filesystem path to the volume.
        template_id (Optional[str]): Associated template ID, if any.
    """

    id: UUID
    name: str
    size: int
    status: str
    path: str
    template_id: Optional[str] = None

    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)


class TemplateData(Template):
    """Schema representing template metadata.

    Attributes:
        name (str): Template name only.
    """

    name: str
