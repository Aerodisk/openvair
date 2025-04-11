from uuid import UUID  # noqa: D100
from typing import Literal, Optional
from pathlib import Path

from pydantic import BaseModel

from openvair.common.base_command_dto import BaseCommandDTO


class CreateTemplateManagerData(BaseModel):  # noqa: D101
    name: str
    description: Optional[str]
    path: Path
    format: Literal['qcow2', 'raw']
    storage_id: UUID
    is_backing: bool


class CreateTemplateMethodData(BaseModel):  # noqa: D101
    source_disk_path: Path


class CreateTemplateDTO(  # noqa: D101
    BaseCommandDTO[CreateTemplateManagerData, CreateTemplateMethodData]
):
    pass


class EditTemplateDTO(BaseModel):  # noqa: D101
    class ManagerData(BaseModel):  # noqa: D106
        name: str
        path: Path
        is_backing: bool
        related_volumes: list

    class MethodData(BaseModel):  # noqa: D106
        new_name: Optional[str]
        description: Optional[str]
