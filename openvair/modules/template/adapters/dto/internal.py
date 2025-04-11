from uuid import UUID  # noqa: D100
from typing import Literal
from pathlib import Path

from pydantic import BaseModel


class VolumeSnapshot(BaseModel):  # noqa: D101
    id: UUID
    path: Path
    format: Literal['qcow2', 'raw']
    size: int


class StorageSnapshot(BaseModel):  # noqa: D101
    id: UUID
    mount_point: Path
    storage_type: str


class CreateTemplateInternalDTO(BaseModel):  # noqa: D101
    volume: VolumeSnapshot
    storage: StorageSnapshot
