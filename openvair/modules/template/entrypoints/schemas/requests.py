"""Request models for template-related API endpoints.

Defines request payload schemas used for creating, updating templates and
creating volumes from templates.
"""

from uuid import UUID
from typing import Literal, Optional

from pydantic import Field

from openvair.common.base_pydantic_models import APIConfigRequestModel


class RequestCreateTemplate(APIConfigRequestModel):
    """Schema for creating a new template.

    Inherits common fields from APITemplateBase and adds the field
    for selecting a base volume from which to create the template.

    Attributes:
        base_volume_id (UUID): ID of the base volume to use for the template.

    Example:
        >>> RequestCreateTemplate(
        ...     name='ubuntu-template',
        ...     storage_id=UUID('...'),
        ...     is_backing=True,
        ...     base_volume_id=UUID('...'),
        ... )
    """

    name: str
    description: Optional[str]
    storage_id: UUID
    base_volume_id: UUID
    is_backing: bool


class RequestEditTemplate(APIConfigRequestModel):
    """Schema for updating a template.

    Requires at least one of the fields to be provided.

    Attributes:
        name (Optional[str]): New name for the template.
        description (Optional[str]): New description.
    """

    name: Optional[str] = Field(None, min_length=1, max_length=40)
    description: Optional[str] = Field(None, max_length=255)


class RequetsCreateVolumeFromTemplate(APIConfigRequestModel):
    """Schema for creating a volume from a template.

    Attributes:
        volume_data (CreateVolume): Parameters for the new volume.
    """

    volume_data: 'CreateVolume'


class CreateVolume(APIConfigRequestModel):
    """Schema for creating a new volume.

    Attributes:
        name (str): The name of the volume.
        description (str): A description of the volume.
        storage_id (UUID): The ID of the storage to create the volume in.
        format (Literal['qcow2', 'raw']): The format of the volume.
        size (int): The size of the volume in bytes.
        read_only (Optional[bool]): Whether the volume is read-only.
    """

    name: str = Field(min_length=1, max_length=40)
    description: str = Field(max_length=255)
    storage_id: UUID
    tmp_format: Literal['qcow2', 'raw']
    size: int = Field(0, ge=1)
    read_only: Optional[bool] = False
