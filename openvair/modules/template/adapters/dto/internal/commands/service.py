from uuid import UUID  # noqa: D100
from typing import ClassVar, Optional

from pydantic import Field, BaseModel, ConfigDict

from openvair.common.configs.pydantic import dto_config


class CreateTemplateServiceCommandDTO(BaseModel):  # noqa: D101
    name: str
    description: Optional[str]
    storage_id: UUID
    base_volume_id: UUID
    is_backing: bool

    model_config: ClassVar[ConfigDict] = dto_config


class GetTemplateServiceCommandDTO(BaseModel):  # noqa: D101
    id: UUID


class EditTemplateServiceCommandDTO(BaseModel):  # noqa: D101
    id: UUID
    name: Optional[str] = Field(min_length=1, max_length=40)
    description: Optional[str]


class DeleteTemplateServiceCommandDTO(BaseModel):  # noqa: D101
    id: UUID
