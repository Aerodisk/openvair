from uuid import UUID  # noqa: D100
from typing import Optional
from pathlib import Path

from pydantic import BaseModel


class CreateVolumeFromTemplateServiceCommandDTO(BaseModel):  # noqa: D101
    name: str
    description: str
    storage_id: UUID
    template_id: UUID
    read_only: Optional[bool]
    user_id: UUID

class CreateVolumeFromTemplateDomainCommandDTO(BaseModel):  # noqa: D101
    template_path: Path
    is_backing: bool

class CreateVolumeCloneServiceCommandDTO(BaseModel):  # noqa: D101
    id: UUID
    name: str
    description: str
    storage_id: UUID
    source_volume_id: UUID
    read_only: Optional[bool]
    path: Path
