from uuid import UUID  # noqa: D100
from typing import Any, Literal
from pathlib import Path

from pydantic import Field, BaseModel, model_validator


class TemplateModelDTO(BaseModel):  # noqa: D101
    id: UUID
    name: str
    description: str | None
    path: Path
    tmp_format: Literal['qcow2', 'raw']
    size: int
    is_backing: bool


class StorageModelDTO(BaseModel):  # noqa: D101
    id: UUID
    name: str
    storage_type: str
    status: str
    available_space: int = Field(..., alias='available')
    storage_extra_specs: dict[str, Any] = Field(default_factory=dict)
    mount_point: str

    @model_validator(mode='before')
    @classmethod
    def extract_mount_point(cls, data: dict) -> dict:  # noqa: D102
        data['mount_point'] = data.get('storage_extra_specs', {}).get(
            'mount_point', ''
        )
        return data
