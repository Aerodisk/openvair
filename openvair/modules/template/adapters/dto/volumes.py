"""DTO models for volume-related operations within the template module.

This module provides data transfer objects used to validate and serialize
volume-related data when interacting between layers (API, service, domain).

Classes:
    - DTOExistingVolume: Represents an existing volume with full metadata.
    - DTOCreateVolume: Represents the payload for creating a new volume.
    - DTOGetVolume: DTO for querying volume by ID.
"""

from uuid import UUID
from typing import Literal, ClassVar, Optional

from pydantic import (
    Field,
    BaseModel,
    ConfigDict,
    field_validator,
)

from openvair.common.configs.pydantic import (
    dto_config,
    lenient_dto_config,
)
from openvair.libs.validation.validators import Validator


class ConfigurationVolumeDTO(BaseModel):
    """Base configuration class for volume DTOs.

    This class defines the shared Pydantic model configuration for all
    volume-related DTOs. It centralizes settings like alias usage,
    validation behavior, and JSON encoding.

    Attributes:
        model_config (ConfigDict): Pydantic configuration for volume DTOs.
    """

    model_config: ClassVar[ConfigDict] = dto_config


class DTOExistingVolume(BaseModel):
    """Schema representing a volume.

    Attributes:
        id (UUID): The ID of the volume.
        name (str): The name of the volume.
        description (Optional[str]): A description of the volume.
        storage_id (Optional[UUID]): The ID of the storage the volume belongs
            to.
        user_id (Optional[UUID]): The ID of the user who owns the volume.
        format (str): The format of the volume (e.g., qcow2, raw).
        size (int): The size of the volume in bytes.
        used (Optional[int]): The amount of space used in the volume.
        status (Optional[str]): The status of the volume.
        information (Optional[str]): Additional information about the volume.
        attachments (List[Optional[Attachment]]): A list of attachments for the
            volume.
        read_only (Optional[bool]): Whether the volume is read-only.
    """

    id: UUID
    name: str
    description: Optional[str] = None
    storage_id: Optional[UUID] = None
    user_id: Optional[UUID] = None
    format: Literal['qcow2', 'raw']
    size: int
    used: Optional[int] = None
    status: Optional[str] = None
    information: Optional[str] = None
    read_only: Optional[bool] = False
    model_config: ClassVar[ConfigDict] = lenient_dto_config


class DTOCreateVolume(ConfigurationVolumeDTO):
    """Schema for creating a new volume.

    Attributes:
        name (str): The name of the volume.
        description (str): A description of the volume.
        storage_id (UUID): The ID of the storage to create the volume in.
        format (Literal['qcow2', 'raw']): The format of the volume.
        size (int): The size of the volume in bytes.
        read_only (Optional[bool]): Whether the volume is read-only.
    """

    name: str = Field(min_length=1, max_length=40)
    description: str = Field(max_length=255)
    storage_id: UUID
    format: Literal['qcow2', 'raw']
    size: int = Field(0, ge=1)
    read_only: Optional[bool] = False

    validate_name = field_validator('name')(
        Validator.special_characters_validate
    )
    validate_description = field_validator('description')(
        Validator.special_characters_validate
    )


class DTOGetVolume(ConfigurationVolumeDTO):
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
