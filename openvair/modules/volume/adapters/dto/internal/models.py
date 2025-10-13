from uuid import UUID  # noqa: D100
from typing import Literal
from pathlib import Path

from pydantic import BaseModel


class ApiAttachmentModelDTO(BaseModel):  # noqa: D101
    id: int
    vm_id: UUID
    target: Path | None = None


class ApiVolumeModelDTO(BaseModel):  # noqa: D101
    id: UUID
    name: str
    description: str | None = None
    storage_id: UUID | None = None
    user_id: UUID | None = None
    format: str
    size: int
    used: int | None = None
    status: str | None = None
    information: str | None = None
    attachments: list[ApiAttachmentModelDTO | None]
    read_only: bool | None = False
    template_id: UUID | None = None


class DomainVolumeManagerDTO(BaseModel):  # noqa: D101
    id: UUID
    format: Literal['qcow2', 'raw']
    size: int
    description: str
    storage_type: str
    path: str


class CreateVolumeFromTemplateModelDTO(BaseModel):  # noqa: D101
    name: str
    description: str | None
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
