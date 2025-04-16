from uuid import UUID  # noqa: D100
from typing import ClassVar, Optional
from pathlib import Path

from pydantic import BaseModel, ConfigDict

from openvair.common.configs.pydantic import dto_config, lenient_dto_config


class CreateTemplateServiceCommandDTO(BaseModel):  # noqa: D101
    name: str
    description: Optional[str]
    storage_id: UUID
    base_volume_id: UUID
    is_backing: bool

    model_config: ClassVar[ConfigDict] = dto_config


class CreateTemplateDomainCommandDTO(BaseModel):  # noqa: D101
    source_disk_path: Path
    model_config: ClassVar[ConfigDict] = lenient_dto_config


class EditTemplateServiceCommandDTO(BaseModel):  # noqa: D101
    id: UUID
    name: Optional[str]
    description: Optional[str]

class EditTemplateDomainCommandDTO(BaseModel):  # noqa: D101
    name:str
