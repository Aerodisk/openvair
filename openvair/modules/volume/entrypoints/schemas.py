"""Pydantic schemas for volume API.

This module defines the Pydantic models (schemas) used for validating and
serializing the data exchanged through the volume-related API endpoints.

Classes:
    Attachment: Schema for representing a volume attachment.
    Volume: Schema for representing a volume.
    CreateVolume: Schema for creating a new volume.
    ExtendVolume: Schema for extending an existing volume.
    EditVolume: Schema for editing a volume's metadata.
    AttachVolume: Schema for attaching a volume to a virtual machine.
    DetachVolume: Schema for detaching a volume from a virtual machine.
    AttachVolumeInfo: Schema for returning information about an attached volume.
"""

from typing import List, Literal, Optional

from pydantic import Field, BaseModel, field_validator

from openvair.modules.tools import validators


class Attachment(BaseModel):
    """Schema representing a volume attachment.

    Attributes:
        id (int): The ID of the attachment.
        vm_id (str): The ID of the virtual machine the volume is attached to.
        target (Optional[str]): The target device path for the attachment.
    """

    id: int
    vm_id: str
    target: Optional[str] = None


class Volume(BaseModel):
    """Schema representing a volume.

    Attributes:
        id (str): The ID of the volume.
        name (str): The name of the volume.
        description (Optional[str]): A description of the volume.
        storage_id (Optional[str]): The ID of the storage the volume belongs to.
        user_id (Optional[str]): The ID of the user who owns the volume.
        format (str): The format of the volume (e.g., qcow2, raw).
        size (int): The size of the volume in bytes.
        used (Optional[int]): The amount of space used in the volume.
        status (Optional[str]): The status of the volume.
        information (Optional[str]): Additional information about the volume.
        attachments (List[Optional[Attachment]]): A list of attachments for the
            volume.
        read_only (Optional[bool]): Whether the volume is read-only.
    """

    id: str
    name: str
    description: Optional[str] = None
    storage_id: Optional[str] = None
    user_id: Optional[str] = None
    format: str
    size: int
    used: Optional[int] = None
    status: Optional[str] = None
    information: Optional[str] = None
    attachments: List[Optional[Attachment]]
    read_only: Optional[bool] = False


class CreateVolume(BaseModel):
    """Schema for creating a new volume.

    Attributes:
        name (str): The name of the volume.
        description (str): A description of the volume.
        storage_id (str): The ID of the storage to create the volume in.
        format (Literal['qcow2', 'raw']): The format of the volume.
        size (int): The size of the volume in bytes.
        read_only (Optional[bool]): Whether the volume is read-only.
    """

    name: str
    description: str
    storage_id: str
    format: Literal['qcow2', 'raw']
    size: int = Field(0, ge=1)
    read_only: Optional[bool] = False

    _normalize_id = field_validator('storage_id')(validators.uuid_validate)

    @field_validator('name')
    @classmethod
    def name_validator(cls, value: str) -> str:
        """Validate the name field."""
        min_length = 1
        max_length = 40
        if len(value) < min_length or len(value) > max_length:
            msg = "Length of name mustn't be 0 and " 'must be lower then 40.'
            raise ValueError(msg)
        validators.special_characters_validate(value)
        return value

    @field_validator('description')
    @classmethod
    def description_validator(cls, value: str) -> str:
        """Validate the description field."""
        max_length = 255
        if len(value) > max_length:
            msg = 'Length of description must be lower then 255.'
            raise ValueError(msg)
        return value


class ExtendVolume(BaseModel):
    """Schema for extending an existing volume.

    Attributes:
        new_size (int): The new size of the volume in bytes.
    """

    new_size: int = Field(0, ge=1)


class EditVolume(BaseModel):
    """Schema for editing a volume's metadata.

    Attributes:
        name (str): The new name of the volume.
        description (str): The new description of the volume.
        read_only (Optional[bool]): Whether the volume is read-only.
    """

    name: str
    description: str
    read_only: Optional[bool] = False

    @field_validator('name')
    @classmethod
    def name_validator(cls, value: str) -> str:
        """Validate the name field."""
        min_length = 1
        max_length = 40
        if len(value) < min_length or len(value) > max_length:
            msg = "Length of name mustn't be 0 and " 'must be lower then 40.'
            raise ValueError(msg)
        validators.special_characters_validate(value)
        return value

    @field_validator('description')
    @classmethod
    def description_validator(cls, value: str) -> str:
        """Validate the description field."""
        max_length = 255
        if len(value) > max_length:
            msg = 'Length of description must be lower then 255.'
            raise ValueError(msg)
        return value


class AttachVolume(BaseModel):
    """Schema for attaching a volume to a virtual machine.

    Attributes:
        vm_id (str): The ID of the virtual machine.
        target (Optional[str]): The target device path for the attachment.
    """

    vm_id: str
    target: Optional[str] = None

    _normalize_id = field_validator('vm_id')(validators.uuid_validate)

    @field_validator('target')
    @classmethod
    def path_validator(cls, value: str) -> str:
        """Validate the target path field."""
        if len(value) < 1:
            msg = 'Length of target must be bigger then 0.'
            raise ValueError(msg)
        validators.special_characters_path_validate(value)
        return value


class DetachVolume(BaseModel):
    """Schema for detaching a volume from a virtual machine.

    Attributes:
        vm_id (str): The ID of the virtual machine.
    """

    vm_id: str

    _normalize_id = field_validator('vm_id')(validators.uuid_validate)


class AttachVolumeInfo(BaseModel):
    """Schema for returning information about an attached volume.

    Attributes:
        path (Optional[str]): The path of the volume.
        size (int): The size of the volume in bytes.
        provisioning (str): The provisioning method of the volume.
    """

    path: Optional[str] = None
    size: int
    provisioning: str
