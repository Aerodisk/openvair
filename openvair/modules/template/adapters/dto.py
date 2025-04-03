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
from typing import ClassVar, Optional
from pathlib import Path
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from openvair.common.configs.pydantic import DTOConfig


class BaseTemplateDTO(BaseModel):
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
    description: Optional[str]
    path: Path
    storage_id: UUID
    is_backing: bool
    model_config: ClassVar[ConfigDict] = ConfigDict(**DTOConfig.model_config)

class TemplateDTO(BaseTemplateDTO):
    """DTO representing a complete template record.

    Includes metadata fields such as ID and creation time.

    Attributes:
        id (UUID): Unique ID of the template.
        created_at (datetime): Timestamp of creation.
    """
    id: UUID
    created_at: datetime


class TemplateCreateCommandDTO(BaseModel):
    """DTO representing a creation command payload for a template.

    Combines template metadata and volume reference needed for logic.
    """

    base_volume_id: UUID
    template: BaseTemplateDTO

    model_config = ConfigDict(**DTOConfig.model_config)


class TemplateEditPayloadDTO(BaseTemplateDTO):
    """DTO used for partial updates to a template.

    Attributes:
        description (Optional[str]): New description, if applicable.
    """

    description: Optional[str] = None
    template: TemplateDTO


class TemplateDataPayloadDTO(BaseTemplateDTO):
    """DTO used for referencing a template by name.

    Includes only the name field. Useful for lightweight links.

    Attributes:
        name (str): Name of the template.
    """
    name: str
    template: TemplateDTO

class VolumeQuery(BaseModel):
    """DTO for querying a volume by its ID.

    This model is used to create a JSON-serializable payload for RPC calls
    that require a volume identifier. It leverages the JSON encoders defined
    in DTOConfig to automatically convert UUID values to strings.

    Attributes:
        volume_id (UUID): Unique identifier of the volume.

    Example:
        >>> from uuid import UUID
        >>> query = VolumeQuery(volume_id=UUID("123e4567-e89b-12d3-a456-426614174000"))
        >>> payload = query.model_dump(mode='json')
        >>> print(payload)  # {'volume_id': '123e4567-e89b-12d3-a456-426614174000'}
    """  # noqa: E501
    volume_id: UUID
    model_config: ClassVar[ConfigDict] = ConfigDict(**DTOConfig.model_config)

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
