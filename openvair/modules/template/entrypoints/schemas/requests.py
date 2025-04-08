"""Request models for template-related API endpoints.

Defines request payload schemas used for creating, updating templates and
creating volumes from templates.
"""

from uuid import UUID
from typing import Optional

from pydantic import Field

# from openvair.modules.template.adapters.dto import CreateVolume
from openvair.modules.template.adapters.dto import CreateVolume
from openvair.modules.template.entrypoints.schemas.base import (
    APIConfigRequestModel,
)


class RequestCreateTemplate(APIConfigRequestModel):
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
    name: str
    description: Optional[str]
    storage_id: UUID
    is_backing: bool


class RequestEditTemplate(APIConfigRequestModel):
    """Schema for updating a template.

    Inherits common fields from BaseTemplate and makes name and description
    optional.

    Attributes:
        name (Optional[str]): New name for the template.
        description (Optional[str]): New description.
    """

    name: str = Field(None, min_length=1, max_length=40)
    description: Optional[str] = Field(None, max_length=255)


class RequetsCreateVolumeFromTemplate(APIConfigRequestModel):
    """Schema for creating a volume from a template.

    Attributes:
        volume_data (CreateVolume): Parameters for the new volume.
    """

    volume_data: CreateVolume
