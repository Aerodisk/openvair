# noqa: D100
from uuid import UUID
from typing import List, Literal, Optional
from pathlib import Path
from datetime import datetime

from openvair.common.base_pydantic_models import BaseDTOModel
from openvair.modules.template.shared.enums import TemplateStatus


class ApiTemplateModelDTO(BaseDTOModel):  # noqa: D101
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


class DomainTemplateModelDTO(BaseDTOModel):  # noqa: D101
    tmp_format: str
    name: str
    path: Path
    related_volumes: Optional[List] = None
    is_backing: bool
    description: str


class CreateTemplateModelDTO(BaseDTOModel):  # noqa: D101
    name: str
    description: Optional[str]
    path: Path
    tmp_format: Literal['qcow2', 'raw']
    storage_id: UUID
    is_backing: bool
