"""DTO definitions for the Template module.

This module provides data transfer objects (DTOs) for operations related to
template management, including creation, editing, deletion, and volume
generation from templates. These DTOs are used for structured communication
between the API, service, and domain layers, particularly over RPC.

Classes:
    - DTOTemplate: Represents a complete template record with metadata.
    - DTOCreateTemplate: Payload for creating a new template.
    - DTOGetTemplate: Request model for fetching a template by ID.
    - DTOEditTemplate: Partial update data for an existing template.
    - DTODeleteTemplate: Request for deleting a template.
    - DTOCreateVolumeFromTemplate: Request to create a volume based on a
        template.
    - TemplateDomain: Placeholder for domain-level template representation.

Dependencies:
    - DTOConfigModel: Base class providing configuration for all DTOs.
    - DTOCreateVolume: Volume specification model used during volume creation
        from templates.
"""

from uuid import UUID
from typing import Dict, Literal, Optional
from pathlib import Path
from datetime import datetime

from pydantic import Field, BaseModel

from openvair.modules.template.shared.enums import TemplateStatus
from openvair.modules.template.adapters.dto.base import DTOConfigModel
from openvair.modules.template.adapters.dto.volumes import DTOCreateVolume


class DTOTemplate(DTOConfigModel):
    """DTO representing a complete template record.

    This data transfer object is used to represent the full state of a
    template, including its metadata, status, size, and file system path.

    Attributes:
        id (Optional[UUID]): Unique ID of the template.
        name (str): Template name.
        description (Optional[str]): Optional description of the template.
        storage_id (UUID): ID of the storage where the template resides.
        is_backing (bool): Indicates if this template is a backing image.
        path (Optional[Path]): Filesystem path to the template image.
        created_at (Optional[datetime]): Timestamp of creation.
        status (Optional[TemplateStatus]): Current template status.
        information (Optional[str]): Additional diagnostic or context info.
        format (Optional[Literal['qcow2', 'raw']]): Format of the image file.
        size (int): Size of the template in bytes.
    """

    id: Optional[UUID] = None
    name: str
    description: Optional[str]
    storage_id: UUID
    is_backing: bool
    path: Optional[Path] = None
    created_at: Optional[datetime] = None
    status: Optional[TemplateStatus] = None
    information: Optional[str] = None
    format: Optional[Literal['qcow2', 'raw']] = 'qcow2'
    size: int = Field(1, ge=1)


class DTOCreateTemplate(DTOConfigModel):
    """DTO representing the payload required to create a template.

    Used as the input for service-layer logic to initiate template creation
    from a base volume.

    Attributes:
        base_volume_id (UUID): The ID of the volume on which to base the
            template.
        name (str): Template name.
        description (Optional[str]): Optional description of the template.
        storage_id (UUID): Target storage ID for the template.
        is_backing (bool): Whether this template should be used as a backing
            file.
    """

    base_volume_id: UUID
    name: str
    description: Optional[str]
    storage_id: UUID
    is_backing: bool


class DTOGetTemplate(DTOConfigModel):
    """DTO for retrieving a template by its ID.

    Used as an RPC payload to request a specific template from the system.

    Attributes:
        id (UUID): Unique identifier of the template to retrieve.

    Example:
        >>> DTOGetTemplate(id=UUID('123e4567-e89b-12d3-a456-426614174000'))
    """

    id: UUID


class DTOEditTemplate(DTOConfigModel):
    """DTO used for editing an existing template.

    Used in service logic for applying partial updates to a template.

    Attributes:
        id (UUID): ID of the template to update.
        name (Optional[str]): New name for the template.
        description (Optional[str]): Updated description of the template.
    """

    id: UUID
    name: Optional[str] = None
    description: Optional[str] = None


class DTODeleteTemplate(DTOConfigModel):
    """DTO for deleting a template by ID.

    Attributes:
        id (UUID): Unique identifier of the template to delete.
    """
    id: UUID


class DTOCreateVolumeFromTemplate(DTOConfigModel):
    """DTO for creating a volume from a template.

    This DTO includes all required information to instantiate a volume
    based on a given template, including volume specs and user context.

    Attributes:
        template_id (UUID): ID of the template to use as the source.
        volume_info (DTOCreateVolume): Configuration of the new volume.
        user_info (Dict): Authenticated user context.
    """
    template_id: UUID
    volume_info: DTOCreateVolume
    user_info: Dict


class TemplateDomain(BaseModel):
    """Placeholder domain model for internal template logic.

    This class is currently a stub and may be extended in the future to
    represent business logic entities within the domain layer.
    """
