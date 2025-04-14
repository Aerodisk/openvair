# noqa: D100
from uuid import UUID
from typing import List, ClassVar, Optional
from pathlib import Path
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from openvair.common.configs.pydantic import dto_config, lenient_dto_config
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


class CreateTemplateInputDTO(BaseModel):  # noqa: D101
    name: str
    description: Optional[str]
    storage_id: UUID
    base_volume_id: UUID
    is_backing: bool

    model_config: ClassVar[ConfigDict] = dto_config
