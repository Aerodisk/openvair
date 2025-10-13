from uuid import UUID  # noqa: D100
from pathlib import Path

from pydantic import BaseModel


class CreateVolumeFromTemplateServiceCommandDTO(BaseModel):  # noqa: D101
    name: str
    description: str
    storage_id: UUID
    template_id: UUID
    read_only: bool | None
    user_id: UUID


class CreateVolumeFromTemplateDomainCommandDTO(BaseModel):  # noqa: D101
    template_path: Path
    is_backing: bool


class CloneVolumeDomainCommandDTO(BaseModel):  # noqa: D101
    mount_point: Path
    new_id: UUID
