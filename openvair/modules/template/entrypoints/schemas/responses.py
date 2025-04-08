"""Response models for template-related API endpoints.

Defines schemas for returning template metadata in API responses.
"""

from uuid import UUID
from typing import Optional
from datetime import datetime

from openvair.modules.template.shared.enums import TemplateStatus
from openvair.modules.template.entrypoints.schemas.base import (
    APIConfigResponseModel,
)


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

    id: UUID
    name: str
    description: Optional[str]
    storage_id: UUID
    is_backing: bool
    created_at: datetime
    status: TemplateStatus
