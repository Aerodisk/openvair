"""Schemas for storage-related API requests and responses.

This module defines the Pydantic models (schemas) used for validating and
serializing the data in the storage-related API endpoints.

Classes:
    NfsStorageExtraSpecsCreate: Schema for creating NFS storage specifications.
    NfsStorageExtraSpecsInfo: Schema for retrieving NFS storage specifications.
    LocalFSStorageExtraSpecsCreate: Schema for creating local FS storage
        specifications.
    LocalFSStorageExtraSpecsInfo: Schema for retrieving local FS storage
        specifications.
    Storage: Schema representing a storage entity.
    CreateStorage: Schema for creating a new storage.
    LocalDisk: Schema representing a local disk entity.
    ListOfLocalDisks: Schema representing a list of local disks.
    CreateLocalPartition: Schema for creating a local disk partition.
    DeleteLocalPartition: Schema for deleting a local disk partition.
"""

import ipaddress
from uuid import UUID
from typing import List, Union, Literal, Optional
from pathlib import Path

from pydantic import (
    Field,
    BaseModel,
    ConfigDict,
    field_validator,
)

from openvair.libs.validation.validators import Validator


class NfsStorageExtraSpecsCreate(BaseModel):
    """Schema for creating NFS storage specifications.

    Attributes:
        ip (str): The IP address of the NFS server.
        path (str): The path to the NFS share on the server.
        mount_version (Optional[str]): The NFS mount version (default is '4').
    """

    ip: ipaddress.IPv4Address
    path: Path = Field(min_length=1)
    mount_version: Literal['3', '4'] = '4'

    validate_path = field_validator('path', mode='before')(
        lambda v: Validator.special_characters_validate(v, allow_slash=True)
    )


class NfsStorageExtraSpecsInfo(NfsStorageExtraSpecsCreate):
    """Schema for retrieving NFS storage specifications.

    Attributes:
        mount_point (Optional[str]): The mount point of the NFS share.
    """

    mount_point: Optional[str] = None


class LocalFSStorageExtraSpecsCreate(BaseModel):
    """Schema for creating local file system storage specifications.

    Attributes:
        path (str): The path to the local storage.
        fs_type (Literal['xfs', 'ext4']): The file system type.
    """

    path: Path = Field(min_length=1)
    fs_type: Literal['xfs', 'ext4']

    validate_path = field_validator('path', mode='before')(
        lambda v: Validator.special_characters_validate(
            str(v), allow_slash=True
        )
    )


class LocalFSStorageExtraSpecsInfo(LocalFSStorageExtraSpecsCreate):
    """Schema for retrieving local file system storage specifications.

    Attributes:
        mount_point (Optional[str]): The mount point of the local storage.
    """

    mount_point: Optional[str] = None


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
    storage_extra_specs: Union[
        NfsStorageExtraSpecsInfo, LocalFSStorageExtraSpecsInfo
    ]


class CreateStorage(BaseModel):
    """Schema for creating a new storage.

    Attributes:
        name (str): The name of the storage.
        description (str): A brief description of the storage.
        storage_type (Literal['nfs', 'localfs']): The type of storage.
        specs (Union[
                NfsStorageExtraSpecsCreate,
                LocalFSStorageExtraSpecsCreate]): Specifications for the
                    storage.
    """

    name: str = Field(min_length=1, max_length=60)
    description: str = Field(max_length=255)
    storage_type: Literal['nfs', 'localfs']
    specs: Union[NfsStorageExtraSpecsCreate, LocalFSStorageExtraSpecsCreate]
    model_config = ConfigDict(extra='forbid')

    validate_name = field_validator('name')(
        Validator.special_characters_validate
    )
    validate_description = field_validator('description')(
        Validator.special_characters_validate
    )


class LocalDisk(BaseModel):
    """Schema representing a local disk entity.

    Attributes:
        path (str): The path to the local disk.
        size (int): The size of the local disk in bytes.
        mountpoint (Optional[str]): The mount point of the local disk.
        fs_uuid (Optional[str]): The file system UUID of the local disk.
        type (Optional[str]): The type of the local disk.
        fstype (Optional[str]): The file system type of the local disk.
        parent (Optional[str]): The parent disk, if applicable.
    """

    path: Path
    size: int
    mountpoint: Optional[str] = None
    fs_uuid: Optional[str] = None
    type: Optional[str] = None
    fstype: Optional[str] = None
    parent: Optional[str] = None


class ListOfLocalDisks(BaseModel):
    """Schema representing a list of local disks.

    Attributes:
        disks (List[Optional[LocalDisk]]): A list of local disks.
    """

    disks: List[Optional[LocalDisk]]


class CreateLocalPartition(BaseModel):
    """Schema for creating a local disk partition.

    Attributes:
        local_disk_path (str): The path to the local disk.
        storage_type (Literal['local_partition']): The type of storage.
        size_value (int): The size of the partition in bytes.
        size_unit (Literal['B']): The unit of the partition size
            (default is 'B').
    """

    local_disk_path: Path
    storage_type: Literal['local_partition']
    size_value: int
    size_unit: Literal['B']


class DeleteLocalPartition(BaseModel):
    """Schema for deleting a local disk partition.

    Attributes:
        storage_type (Literal['local_partition']): The type of storage.
        local_disk_path (str): The path to the local disk.
        partition_number (str): The number of the partition to delete.
    """

    storage_type: Literal['local_partition']
    local_disk_path: Path
    partition_number: str
