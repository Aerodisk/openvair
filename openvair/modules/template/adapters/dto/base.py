# from uuid import UUID  # noqa: D100
# from typing import ClassVar, Optional

from typing import ClassVar

from pydantic import (
    BaseModel,
    ConfigDict,
)

from openvair.common.configs.pydantic import dto_config


class DTOConfigModel(BaseModel):
    """Base class for all DTO models in the template module.

    Applies global Pydantic configuration via `DTOConfig`.

    Purpose:
        - Provides shared model settings for validation and serialization.
        - Inherited by all specific DTOs used in the service layer.

    Note:
        This class should not be instantiated directly.
    """

    model_config: ClassVar[ConfigDict] = dto_config
