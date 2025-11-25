"""DTOs for internal service-layer command operations.

This module provides command objects used to describe service and domain-level
operations on templates (create, edit, delete).
"""

from uuid import UUID
from typing import Optional
from pathlib import Path

from pydantic import Field

from openvair.common.base_pydantic_models import BaseDTOModel


class GetTemplateServiceCommandDTO(BaseDTOModel):
    """DTO for retrieving a template by its ID.

    Attributes:
        id (UUID): Unique identifier of the template.
    """

    id: UUID


class CreateTemplateServiceCommandDTO(BaseDTOModel):
    """DTO for creating a template at the service layer.

    Contains metadata required to register a new template in the system.

    Attributes:
        name (str): Name of the new template.
        description (Optional[str]): Optional description.
        storage_id (UUID): Storage where the template will be located.
        base_volume_id (UUID): ID of the volume used to create the template.
        is_backing (bool): Whether the template acts as a backing image.
    """

    name: str
    description: Optional[str]
    storage_id: UUID
    base_volume_id: UUID
    is_backing: bool


class AsyncCreateTemplateServiceCommandDTO(BaseDTOModel):
    """DTO for initiating asynchronous creation of a template.

    Used to trigger domain-level template creation from an existing disk.

    Attributes:
        id (UUID): ID of the template.
        source_disk_path (Path): Filesystem path to the source disk image.
    """

    id: UUID
    source_disk_path: Path


class CreateTemplateDomainCommandDTO(BaseDTOModel):
    """DTO for domain-level template creation.

    Attributes:
        source_disk_path (Path): Path to the disk image used to create the
            template.
    """

    source_disk_path: Path


class EditTemplateServiceCommandDTO(BaseDTOModel):
    """DTO for updating template fields at the service layer.

    Attributes:
        id (UUID): ID of the template to edit.
        name (Optional[str]): New name of the template (if provided).
        description (Optional[str]): New description (if provided).
    """

    id: UUID
    name: Optional[str] = Field(min_length=1, max_length=40)
    description: Optional[str]


class EditTemplateDomainCommandDTO(BaseDTOModel):
    """DTO for editing template metadata at the domain level.

    Attributes:
        name (Optional[str]): New name of the template (if provided).
        description (Optional[str]): New description (if provided).
    """

    name: Optional[str]
    description: Optional[str]


class DeleteTemplateServiceCommandDTO(BaseDTOModel):
    """DTO for deleting a template at the service layer.

    Attributes:
        id (UUID): ID of the template to delete.
    """

    id: UUID
