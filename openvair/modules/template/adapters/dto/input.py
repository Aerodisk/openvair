# noqa: D100
from uuid import UUID
from typing import ClassVar, Optional

from pydantic import BaseModel, ConfigDict

from openvair.common.configs.pydantic import dto_config


class CreateTemplateInputDTO(BaseModel):  # noqa: D101
    name: str
    description: Optional[str]
    storage_id: UUID
    base_volume_id: UUID
    is_backing: bool

    model_config: ClassVar[ConfigDict] = dto_config
