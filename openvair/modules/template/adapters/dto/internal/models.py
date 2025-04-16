# noqa: D100
from uuid import UUID
from typing import List, Literal, ClassVar, Optional
from pathlib import Path
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from openvair.common.configs.pydantic import lenient_dto_config
from openvair.modules.template.shared.enums import TemplateStatus


class ApiTemplateViewDTO(BaseModel):  # noqa: D101
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


class DomainTemplateManagerDTO(BaseModel):  # noqa: D101
    tmp_format: str
    name: str
    path: Path
    related_volumes: Optional[List] = None
    is_backing: bool

    model_config: ClassVar[ConfigDict] = lenient_dto_config


class CreateTemplateDTO(BaseModel):  # noqa: D101
    name: str
    description: Optional[str]
    path: Path
    tmp_format: Literal['qcow2', 'raw']
    storage_id: UUID
    is_backing: bool
    source_disk_path: Path


class EditTemplateDTO(BaseModel):  # noqa: D101
    name: Optional[str]
    description: Optional[str]
