from uuid import UUID  # noqa: D100
from typing import ClassVar, Optional
from pathlib import Path

from pydantic import BaseModel, ConfigDict

from openvair.common.configs.pydantic import lenient_dto_config


class CreateTemplateDomainCommandDTO(BaseModel):  # noqa: D101
    source_disk_path: Path
    model_config: ClassVar[ConfigDict] = lenient_dto_config


class EditTemplateDomainCommandDTO(BaseModel):  # noqa: D101
    name: str
    description: Optional[str]


class DeleteTemplateDomainCommandDTO(BaseModel):  # noqa: D101
    id: UUID
