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


class CloneVolumeDomainCommandDTO(BaseModel):  # noqa: D101
    target_path: Path
