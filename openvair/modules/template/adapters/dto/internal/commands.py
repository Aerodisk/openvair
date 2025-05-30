from uuid import UUID  # noqa: D100
from typing import Optional
from pathlib import Path

from pydantic import Field

from openvair.common.base_pydantic_models import BaseDTOModel


class GetTemplateServiceCommandDTO(BaseDTOModel):  # noqa: D101
    id: UUID


class CreateTemplateServiceCommandDTO(BaseDTOModel):  # noqa: D101
    name: str
    description: Optional[str]
    storage_id: UUID
    base_volume_id: UUID
    is_backing: bool


class AsyncCreateTemplateServiceCommandDTO(BaseDTOModel):  # noqa: D101
    id: UUID
    source_disk_path: Path


class CreateTemplateDomainCommandDTO(BaseDTOModel):  # noqa: D101
    source_disk_path: Path


class EditTemplateServiceCommandDTO(BaseDTOModel):  # noqa: D101
    id: UUID
    name: Optional[str] = Field(min_length=1, max_length=40)
    description: Optional[str]


class EditTemplateDomainCommandDTO(BaseDTOModel):  # noqa: D101
    name: Optional[str]
    description: Optional[str]


class DeleteTemplateServiceCommandDTO(BaseDTOModel):  # noqa: D101
    id: UUID
