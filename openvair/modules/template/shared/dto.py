"""DTO models for the Template module.

This module defines Pydantic-based DTOs used to transfer
and validate data between the ORM and external layers.

Classes:
    - TemplateDTO: DTO for Template ORM model.

Example:
    orm = Template(...)
    dto = TemplateSerializer.to_dto(orm)
"""

from uuid import UUID
from typing import Optional
from pathlib import Path
from datetime import datetime

from openvair.common.serialization.base_dto import BaseDTO


class TemplateDTO(BaseDTO):
    """DTO representing a template object.

    Attributes:
        id (UUID): Template ID.
        name (str): Template name.
        description (Optional[str]): Description.
        path (Path): Filesystem path.
        storage_id (UUID): ID of associated storage.
        created_at (datetime): Creation timestamp.
        is_backing (bool): Whether it's a backing image.

    Example:
        TemplateDTO(
            id=UUID("..."),
            name="base-template",
            path=Path("/path.qcow2"),
            storage_id=UUID("..."),
            created_at=datetime.utcnow(),
            is_backing=True
        )
    """

    id: UUID
    name: str
    description: Optional[str]
    path: Path
    storage_id: UUID
    created_at: datetime
    is_backing: bool
