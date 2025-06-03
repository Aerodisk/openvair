"""Response models for template API endpoints.

Defines schemas used to serialize and return template metadata from the API.

Classes:
    - TemplateResponse: Full representation of a template in API responses.
"""

from uuid import UUID
from typing import Optional
from datetime import datetime

from pydantic import Field

from openvair.common.base_pydantic_models import APIConfigResponseModel
from openvair.modules.template.shared.enums import TemplateStatus


class TemplateResponse(APIConfigResponseModel):
    """Schema representing a full template object for API responses.

    Extends:
        APIConfigResponseModel

    Attributes:
        id (UUID): Unique identifier of the template.
        name (str): Name of the template.
        description (Optional[str]): Description of the template.
        storage_id (UUID): Linked storage ID.
        is_backing (bool): Whether it's a backing image.
        created_at (datetime): Timestamp of creation.
        status (TemplateStatus): Current lifecycle status of the template.
    """

    id: UUID = Field(
        ...,
        examples=['a73f920b-d282-41e4-8ec1-6e6b89d3a9e7'],
        description='Unique identifier of the template',
    )
    name: str = Field(
        ..., examples=['ubuntu-template'], description='Name of the template'
    )
    description: Optional[str] = Field(
        None,
        examples=['Template for Ubuntu server deployments'],
        description='Description of the template',
    )
    tmp_format: str = Field(
        ...,
        examples=['qcow2'],
        description='Disk format of the template (qcow2)',
    )
    storage_id: UUID = Field(
        ...,
        examples=['c2f7b67e-92a3-41ea-b760-ef7785ebfcb9'],
        description='ID of the storage where the template resides',
    )
    is_backing: bool = Field(
        ...,
        examples=[True],
        description='Whether this template is a backing image',
    )
    created_at: datetime = Field(
        ...,
        examples=['2024-05-28T10:45:21.000Z'],
        description='Template creation timestamp',
    )
    status: TemplateStatus = Field(
        ...,
        examples=['available'],
        description='Current lifecycle status of the template',
    )
