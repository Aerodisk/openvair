  # noqa: D100
from typing import List, ClassVar, Optional
from pathlib import Path

from pydantic import BaseModel, ConfigDict

from openvair.common.configs.pydantic import lenient_dto_config


class DomainTemplateManagerDTO(BaseModel):  # noqa: D101
    tmp_format: str
    name: str
    path: Path
    related_volumes: Optional[List] = None
    is_backing: bool

    model_config: ClassVar[ConfigDict] = lenient_dto_config
