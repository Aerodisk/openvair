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
from openvair.modules.template.adapters.dto import CreateVolume
from openvair.modules.template.shared.enums import TemplateStatus


class BaseTemplate(BaseModel):
    """Base schema for template-related API operations.

    Contains fields shared by multiple API models (create, edit, etc).

    Attributes:
        name (str): Name of the template.
        description (Optional[str]): Optional description of the template.
        path (Path): Filesystem path to the template image.
        storage_id (UUID): ID of the associated storage.
        is_backing (bool): Whether the template is a backing image.
    """

    name: str
    description: Optional[str]
    path: Path
    storage_id: UUID
    is_backing: bool

    model_config: ClassVar[ConfigDict] = ConfigDict(**APIConfig.model_config)


class Template(BaseTemplate):
    """Schema representing a full template object for API responses.

    Extends `BaseTemplate` with metadata fields typically present in
    a persisted template entity.

    Attributes:
        id (UUID): Unique identifier of the template.
        created_at (datetime): Creation timestamp of the template.

    Example:
        >>> Template(
        ...     id=UUID("..."),
        ...     name="base-template",
        ...     description="Ubuntu 22.04 image",
        ...     path=Path("/mnt/ubuntu.qcow2"),
        ...     storage_id=UUID("..."),
        ...     is_backing=True,
        ...     created_at=datetime.utcnow(),
        ... )
    """
    id: UUID
    created_at: datetime
    status: TemplateStatus


class CreateTemplate(BaseTemplate):
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


class EditTemplate(BaseModel):
    """Schema for updating a template.

    Inherits common fields from BaseTemplate and makes name and description
    optional.

    Attributes:
        name (Optional[str]): New name for the template.
        description (Optional[str]): New description.
    """
    name: str = Field(None, min_length=1, max_length=40)
    description: Optional[str] = Field(None, max_length=255)


class CreateVolumeFromTemplate(CreateVolume):
    """Schema for creating a volume from a template.

    Includes fields required to define the new volume.

    Attributes:
        name (str): Desired name for the volume.
        size (int): Size of the volume in bytes.
    """
    ...

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


class TemplateData(BaseTemplate):
    """Schema for simplified template reference.

    Contains only the name field to identify or link templates.

    Attributes:
        name (str): Template name.
    """

    name: str
