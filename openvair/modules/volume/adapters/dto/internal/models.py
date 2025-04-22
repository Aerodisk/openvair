from uuid import UUID  # noqa: D100
from typing import Literal, Optional
from pathlib import Path

from pydantic import BaseModel


class DomainVolumeManagerDTO(BaseModel):  # noqa: D101
    id: UUID
    format: Literal['qcow2', 'raw']
    size: int
    description: str
    storage_type: str
    path: str


class CreateVolumeFromTemplateDTO(BaseModel):  # noqa: D101
    name: str
    description: Optional[str]
    path: str
    format: Literal['qcow2', 'raw']
    storage_id: UUID
    size: int
    user_id: UUID
    read_only: bool
    storage_type: str
    template_path: Path
    is_backing: bool
    template_id: UUID
