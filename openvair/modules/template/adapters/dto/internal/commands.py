from uuid import UUID  # noqa: D100
from typing import Literal, ClassVar, Optional
from pathlib import Path

from pydantic import BaseModel, ConfigDict

from openvair.common.configs.pydantic import lenient_dto_config


class CreateTemplateDomainCommandDTO(BaseModel):  # noqa: D101
    source_disk_path: Path
    model_config: ClassVar[ConfigDict] = lenient_dto_config


class CreateTemplateServiceCommandDTO(BaseModel):  # noqa: D101
    name: str
    description: Optional[str]
    path: Path
    tmp_format: Literal['qcow2', 'raw']
    storage_id: UUID
    is_backing: bool
    source_disk_path: Path


class EditTemplateCommandDTO(BaseModel):  # noqa: D101
    class ManagerData(BaseModel):  # noqa: D106
        name: str
        path: Path
        is_backing: bool
        related_volumes: list

    class MethodData(BaseModel):  # noqa: D106
        new_name: Optional[str]
        description: Optional[str]
