"""Request models for template API operations.

Defines schemas used as input payloads for template-related API endpoints.
These models represent user-submitted data for creating or modifying templates,
and for creating volumes based on templates.

Classes:
    - RequestCreateTemplate
    - RequestEditTemplate
    - RequetsCreateVolumeFromTemplate
    - CreateVolume
"""

from uuid import UUID

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

    name: str = Field(
        ...,
        examples=['ubuntu-template'],
        description='Name for the new template',
        min_length=1,
        max_length=40,
    )
    description: str | None = Field(
        None,
        examples=['Template for Ubuntu server deployments'],
        description='Optional description for the template',
        max_length=255,
    )
    storage_id: UUID = Field(
        ...,
        examples=['c2f7b67e-92a3-41ea-b760-ef7785ebfcb9'],
        description='ID of the storage where the template will be stored',
    )
    base_volume_id: UUID = Field(
        ...,
        examples=['6d8e34e7-0ef3-4477-8b7e-7b7d4c3e5b91'],
        description=(
            'ID of the base volume from which the template will be created'
        ),
    )
    is_backing: bool = Field(
        ...,
        examples=[True],
        description=(
            'Indicates if the template should be used as a backing image'
        ),
    )


class RequestEditTemplate(APIConfigRequestModel):
    """Schema for updating a template.

    Requires at least one of the fields to be provided.

    Attributes:
        name (Optional[str]): New name for the template.
        description (Optional[str]): New description.
    """

    name: str | None = Field(
        None,
        examples=['ubuntu-template-renamed'],
        description='New name for the template',
        min_length=1,
        max_length=40,
    )
    description: str | None = Field(
        None,
        examples=['Updated description for Ubuntu template'],
        description='New description for the template',
        max_length=255,
    )
