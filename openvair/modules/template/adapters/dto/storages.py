"""DTO models for storage-related operations within the template module.

This module provides data transfer objects for describing storage entities
and for querying storages by ID.

Classes:
    - DTOStorage: Full schema representing a storage object.
    - DTOGetStorage: DTO for querying a specific storage by ID.
"""

from uuid import UUID
from typing import Any, Dict, ClassVar, Optional
from pathlib import Path

from pydantic import (
    BaseModel,
    ConfigDict,
    model_validator,
)

from openvair.common.configs.pydantic import dto_config, lenient_dto_config


class ConfigurationStoragesDTO(BaseModel):
    """Base configuration class for storage DTOs.

    This class defines the shared Pydantic model configuration for all
    storage-related DTOs. It ensures consistent behavior across DTOs
    such as field validation, alias handling, and export settings.

    Attributes:
        model_config (ConfigDict): Pydantic configuration for storage DTOs.
    """

    model_config: ClassVar[ConfigDict] = dto_config


class DTOExistingStorageStorage(BaseModel):
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

    model_config: ClassVar[ConfigDict] = lenient_dto_config

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


class DTOGetStorage(ConfigurationStoragesDTO):
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
