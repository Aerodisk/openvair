from uuid import UUID  # noqa: D100
from typing import ClassVar

from pydantic import BaseModel, ConfigDict

from openvair.common.configs.pydantic_config import dto_config


class GetVolumeCommandDTO(BaseModel):
    """DTO for querying a volume by its ID.

    This model is used to create a JSON-serializable payload for RPC calls
    that require a volume identifier. It leverages the JSON encoders defined
    in DTOConfig to automatically convert UUID values to strings.

    Attributes:
        volume_id (UUID): Unique identifier of the volume.

    Example:
        >>> from uuid import UUID
        >>> query = VolumeQuery(volume_id=UUID('123e4567-e89b-12d3-a456-426614174000'))
        >>> payload = query.model_dump(mode='json')
        >>> print(payload)  # {'volume_id': '123e4567-e89b-12d3-a456-426614174000'}
    """  # noqa: E501

    volume_id: UUID
    model_config: ClassVar[ConfigDict] = dto_config


class GetStorageCommandDTO(BaseModel):
    """DTO for querying a storage by its ID.

    This model is used to create a JSON-serializable payload for RPC calls
    that require a storage identifier. It leverages the JSON encoders defined
    in DTOConfig to automatically convert UUID values to strings.

    Attributes:
        storage_id (UUID): Unique identifier of the volume.

    Example:
        >>> from uuid import UUID
        >>> query = VolumeQuery(storage_id=UUID('123e4567-e89b-12d3-a456-426614174000'))
        >>> payload = query.model_dump(mode='json')
        >>> print(payload)  # {'storage_id': '123e4567-e89b-12d3-a456-426614174000'}
    """  # noqa: E501

    storage_id: UUID
    model_config: ClassVar[ConfigDict] = dto_config
