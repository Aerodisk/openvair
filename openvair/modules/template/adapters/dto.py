"""DTO models for the Template module.

This module defines Pydantic-based DTOs used to transfer
and validate data between the ORM and external layers.

Classes:
    - TemplateDTO: DTO for Template ORM model.
    - TemplateCreateDTO: DTO for creating templates.
    - TemplateEditDTO: DTO for editing templates.
    - TemplateDataDTO: Lightweight DTO with only name field.

Example:
    orm = Template(...)
    dto = TemplateSerializer.to_dto(orm)
"""

from uuid import UUID
from typing import Any, Dict, Literal, ClassVar, Optional
from pathlib import Path
from datetime import datetime

from pydantic import (
    Field,
    BaseModel,
    ConfigDict,
    field_validator,
    model_validator,
)

from openvair.common.configs.pydantic import DTOConfig
from openvair.libs.validation.validators import Validator
from openvair.modules.template.shared.enums import TemplateStatus


class BaseDTO(BaseModel):
    """Base class for all DTO models in the template module.

    Applies global Pydantic configuration via `DTOConfig`.

    Purpose:
        - Provides shared model settings for validation and serialization.
        - Inherited by all specific DTOs used in the service layer.

    Note:
        This class should not be instantiated directly.
    """

    model_config: ClassVar[ConfigDict] = ConfigDict(**DTOConfig.model_config)


class BaseTemplateDTO(BaseDTO):
    """Base DTO for the template entity.

    Contains core fields used across Template-related DTOs.

    Attributes:
        name (str): Name of the template.
        description (Optional[str]): Description of the template.
        path (Path): Filesystem path to the template.
        storage_id (UUID): ID of the associated storage backend.
        is_backing (bool): Whether it's a backing image.

    Example:
        >>> BaseTemplateDTO(
        ...     name='base-template',
        ...     path=Path('/mnt/template.qcow2'),
        ...     storage_id=UUID('...'),
        ...     is_backing=True,
        ... )
    """

    name: str
    description: Optional[str] = None
    storage_id: UUID
    is_backing: bool


class TemplateDTO(BaseTemplateDTO):
    """DTO representing a complete template record.

    Includes metadata fields such as ID and creation time.

    Attributes:
        id (UUID): Unique ID of the template.
        created_at (datetime): Timestamp of creation.
    """

    id: Optional[UUID] = None
    path: Optional[Path] = None
    created_at: Optional[datetime] = None
    status: Optional[TemplateStatus] = None
    information: Optional[str] = None
    format: Optional[Literal['qcow2', 'raw']] = 'qcow2'
    size: int = Field(1, ge=1)


class TemplateCreateCommandDTO(BaseDTO):
    """DTO representing a creation command payload for a template.

    Combines template metadata and volume reference needed for logic.
    """

    base_volume_id: UUID
    template: TemplateDTO


class TemplateGetCommandDTO(BaseDTO):
    """DTO for retrieving a template by its ID.

    Used as input for service-layer logic that fetches a single template.

    Attributes:
        id (UUID): Unique identifier of the template to retrieve.

    Example:
        >>> TemplateGetCommandDTO(id=UUID('...'))
    """

    id: UUID


class TemplateEditCommandDTO(BaseDTO):
    """DTO used for partial updates to a template.

    Attributes:
        description (Optional[str]): New description, if applicable.
    """

    id: UUID
    name: Optional[str] = None
    description: Optional[str] = None


class TemplateDeleteCommandDTO(BaseDTO):  # noqa: D101
    id: UUID


class CreateVolumeInfo(BaseDTO):  # noqa: D101
    name: str = Field(min_length=1, max_length=40)
    description: str = Field(default='', max_length=255)
    storage_id: UUID
    read_only: Optional[bool] = False


class CreateVolumeFromTemplateCommandDTO(BaseDTO):  # noqa: D101
    template_id: UUID
    volume_info: CreateVolumeInfo
    user_info: Dict


class CreateVolume(BaseDTO):
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
    user_info: Dict

    validate_name = field_validator('name')(
        Validator.special_characters_validate
    )
    validate_description = field_validator('description')(
        Validator.special_characters_validate
    )

class Storage(BaseModel):
    """Schema representing a storage entity.

    Attributes:
        id (UUID): The unique identifier of the storage.
        name (str): The name of the storage.
        description (Optional[str]): A brief description of the storage.
        storage_type (str): The type of storage (e.g., 'nfs', 'localfs').
        status (str): The current status of the storage.
        size (int): The total size of the storage in bytes.
        available (int): The available size of the storage in bytes.
        user_id (Optional[UUID]): The ID of the user who owns the storage.
        information (Optional[str]): Additional information about the storage.
        storage_extra_specs (Union[NfsStorageExtraSpecsInfo,
            LocalFSStorageExtraSpecsInfo]): Additional specifications for the
            storage.
    """

    id: UUID
    name: str
    description: Optional[str] = None
    storage_type: str
    status: str
    size: int
    available: int
    user_id: Optional[UUID] = None
    information: Optional[str] = None
    mount_point: Path

    @model_validator(mode='before')
    @classmethod
    def extract_mount_point(cls, values: Dict[str, Any]) -> Dict[str, Any]:  # noqa: C901
        """Pre-validation:

        Extracts the 'mount_point' from the 'storage_extra_specs'
        field if present and sets it as the 'mount_point' field.

        Args:
            values (Dict[str, Any]): The input data dictionary.

        Returns:
            Dict[str, Any]: The modified data dictionary with 'mount_point' set.
        """
        specs = values.get('storage_extra_specs')
        if specs:
            mount = None
            if isinstance(specs, dict):
                mount = specs.get('mount_point')
            elif isinstance(specs, list):
                for spec in specs:
                    if isinstance(spec, dict) and spec.get('mount_point'):
                        mount = spec.get('mount_point')
                        break
            if mount is not None:
                values['mount_point'] = (
                    mount if isinstance(mount, Path) else Path(mount)
                )
        return values


class Volume(BaseModel):
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

class VolumeQuery(BaseModel):
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
    model_config: ClassVar[ConfigDict] = ConfigDict(**DTOConfig.model_config)


class VolumeGettingDTO(BaseDTO):  # noqa: D101
    format: Literal['qcow2', 'raw']
    size: int = Field(0, ge=1)
    used: int


class StorageQuery(BaseModel):
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
    model_config: ClassVar[ConfigDict] = ConfigDict(**DTOConfig.model_config)

class TemplateDomain(BaseModel):  # noqa: D101
    ...
