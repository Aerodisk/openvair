"""Pydantic schemas for the template module.

This module defines data validation and serialization models used in the
template API and service layer.

Schemas:
    - BaseTemplate: Shared fields for template data.
    - CreateTemplate: Schema for creating a new template.
    - Template: Full representation of a template, including metadata.
    - EditTemplate: Schema for partial template updates.
    - CreateVolumeFromTemplate: Payload for creating a volume from a template.
    - Volume: Representation of a volume created from a template.
"""

from uuid import UUID
from typing import ClassVar, Optional
from pathlib import Path
from datetime import datetime

from pydantic import Field, BaseModel, ConfigDict


class BaseTemplate(BaseModel):
    """Base schema for template data.

    Shared fields used for both input and output operations.

    Attributes:
        name (str): Template name.
        description (Optional[str]): Optional description.
        path (Path): Filesystem path to the template.
        storage_id (UUID): Associated storage identifier.
        is_backing (bool): Indicates whether the template is a backing image.
    """
    name: str = Field(..., min_length=1, max_length=40)
    description: Optional[str] = Field(None, max_length=255)
    path: Path
    storage_id: UUID
    is_backing: bool


class CreateTemplate(BaseTemplate):
    """Schema for creating a new template.

    Attributes:
        base_volume_id (UUID): ID of the base volume to use for the template.
    """
    base_volume_id: UUID = Field(
        ..., description='Идентификатор базового volume для создания шаблона'
    )


class Template(BaseTemplate):
    """Schema representing a template with metadata.

    Attributes:
        id (UUID): Unique identifier of the template.
        created_at (datetime): Timestamp of template creation.
    """
    id: UUID
    created_at: datetime

    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)




class EditTemplate(BaseModel):
    """Schema for updating a template.

    Attributes:
        name (Optional[str]): New name of the template.
        description (Optional[str]): New description of the template.
    """
    name: Optional[str] = Field(None, min_length=1, max_length=40)
    description: Optional[str] = Field(None, max_length=255)


class CreateVolumeFromTemplate(BaseModel):
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

class TemplateData(BaseTemplate):
    """Schema representing template metadata."""

    name: str
