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

from pydantic import BaseModel, ConfigDict, field_validator

from openvair.libs.validation import validators


class NfsStorageExtraSpecsCreate(BaseModel):
    """Schema for creating NFS storage specifications.

    Attributes:
        ip (str): The IP address of the NFS server.
        path (str): The path to the NFS share on the server.
        mount_version (Optional[str]): The NFS mount version (default is '4').
    """

    ip: str
    path: str
    mount_version: Optional[str] = '4'

    @field_validator('mount_version')
    @classmethod
    def mount_version_must_be_3_or_4(cls, value: str) -> str:
        """Validate that the mount version is either 3 or 4."""
        if value not in ('3', '4'):
            msg = 'Mount version must be 3 or 4.'
            raise ValueError(msg)
        return value

    @field_validator('ip')
    @classmethod
    def ip_validator(cls, value: str) -> str:
        """Validate that the provided IP address is valid."""
        ipaddress.ip_address(value)
        return value

    @field_validator('path')
    @classmethod
    def path_validator(cls, value: str) -> str:
        """Validate that the path is non-empty and has no special characters."""
        if len(value) < 1:
            msg = 'Length of target must be greater than 0.'
            raise ValueError(msg)
        validators.special_characters_path_validate(value)
        return value


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

    path: str
    fs_type: Literal['xfs', 'ext4']

    @field_validator('path')
    @classmethod
    def path_validator(cls, value: str) -> str:
        """Validate that the path is non-empty and has no special characters."""
        if len(value) < 1:
            msg = 'Length of target must be greater than 0.'
            raise ValueError(msg)
        validators.special_characters_path_validate(value)
        return value


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
        user_id (Optional[str]): The ID of the user who owns the storage.
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
    user_id: Optional[str] = None
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

    name: str
    description: str
    storage_type: Literal['nfs', 'localfs']
    specs: Union[NfsStorageExtraSpecsCreate, LocalFSStorageExtraSpecsCreate]
    model_config = ConfigDict(extra='forbid')

    @field_validator('name')
    @classmethod
    def name_validator(cls, value: str) -> str:
        """Validate that the name length and its has no special characters."""
        min_length = 1
        max_length = 60
        if len(value) < min_length or len(value) > max_length:
            msg = "Length of name mustn't be 0 and must be lower than 40."
            raise ValueError(msg)
        validators.special_characters_validate(value)
        return value

    @field_validator('description')
    @classmethod
    def description_validator(cls, value: str) -> str:
        """Validate that the description length is appropriate."""
        max_length = 255
        if len(value) > max_length:
            msg = 'Length of description must be lower than 255.'
            raise ValueError(msg)
        validators.special_characters_validate(value)
        return value


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

    path: str
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

    local_disk_path: str
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
    local_disk_path: str
    partition_number: str
