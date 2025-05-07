# noqa: D100
from uuid import UUID
from typing import List, Literal, Optional
from pathlib import Path
from datetime import datetime

from pydantic import BaseModel

from openvair.modules.template.shared.enums import TemplateStatus


class ApiTemplateModel(BaseModel):  # noqa: D101
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


class DomainTemplateModel(BaseModel):  # noqa: D101
    tmp_format: str
    name: str
    path: Path
    related_volumes: Optional[List] = None
    is_backing: bool
    description: str


class CreateTemplateModel(BaseModel):  # noqa: D101
    name: str
    description: Optional[str]
    path: Path
    tmp_format: Literal['qcow2', 'raw']
    storage_id: UUID
    is_backing: bool
