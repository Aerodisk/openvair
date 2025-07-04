from uuid import UUID  # noqa: D100
from typing import List, Literal, Optional
from pathlib import Path

from pydantic import BaseModel


class ApiAttachmentModelDTO(BaseModel):  # noqa: D101
    id: int
    vm_id: UUID
    target: Optional[Path] = None


class ApiVolumeModelDTO(BaseModel):  # noqa: D101
    id: UUID
    name: str
    description: Optional[str] = None
    storage_id: Optional[UUID] = None
    user_id: Optional[UUID] = None
    format: str
    size: int
    used: Optional[int] = None
    status: Optional[str] = None
    information: Optional[str] = None
    attachments: List[Optional[ApiAttachmentModelDTO]]
    read_only: Optional[bool] = False
    template_id: Optional[UUID] = None


class DomainVolumeManagerDTO(BaseModel):  # noqa: D101
    id: UUID
    format: Literal['qcow2', 'raw']
    size: int
    description: str
    storage_type: str
    path: str


class CreateVolumeFromTemplateModelDTO(BaseModel):  # noqa: D101
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
