from uuid import UUID  # noqa: D100
from typing import Optional
from pathlib import Path
from datetime import datetime

from pydantic import BaseModel

from openvair.modules.template.shared.enums import TemplateStatus


class TemplateViewDTO(BaseModel):  # noqa: D101
    id: UUID
    name: str
    description: Optional[str]
    path: Path
    tmp_format: str
    size: int
    status: TemplateStatus
    is_backing: bool
    created_at: datetime
    storage_id: UUID
