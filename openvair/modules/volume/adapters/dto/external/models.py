from uuid import UUID  # noqa: D100
from typing import Any, Dict, Literal, Optional
from pathlib import Path

from pydantic import Field, BaseModel, model_validator


class TemplateModelDTO(BaseModel):  # noqa: D101
    id: UUID
    name: str
    description: Optional[str]
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
    storage_extra_specs: Dict[str, Any] = Field(default_factory=Dict)
    mount_point: str

    @model_validator(mode='before')
    @classmethod
    def extract_mount_point(cls, data: Dict) -> Dict:  # noqa: D102
        data['mount_point'] = data.get('storage_extra_specs', {}).get(
            'mount_point', ''
        )
        return data
