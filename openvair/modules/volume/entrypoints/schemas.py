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

from uuid import UUID
from typing import List, Literal, Optional
from pathlib import Path

from pydantic import Field, BaseModel, field_validator

from openvair.libs.validation.validators import Validator


class Attachment(BaseModel):
    """Schema representing a volume attachment.

    Attributes:
        id (int): The ID of the attachment.
        vm_id (UUID): The ID of the virtual machine the volume is attached to.
        target (Optional[str]): The target device path for the attachment.
    """

    id: int
    vm_id: UUID
    target: Optional[Path] = None


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
    format: str
    size: int
    used: Optional[int] = None
    status: Optional[str] = None
    information: Optional[str] = None
    attachments: List[Optional[Attachment]]
    read_only: Optional[bool] = False
    template_id: Optional[UUID]

class CreateVolume(BaseModel):
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


class CreateVolumeFromTemplate(BaseModel):  # noqa: D101

    name: str = Field(min_length=1, max_length=40)
    description: str = Field(max_length=255)
    storage_id: UUID
    template_id: UUID
    # берем из Template
    # format: Literal['qcow2', 'raw']
    # size: int = Field(0, ge=1)
    read_only: Optional[bool] = False

    validate_name = field_validator('name')(
        Validator.special_characters_validate
    )
    validate_description = field_validator('description')(
        Validator.special_characters_validate
    )

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

    name: str = Field(min_length=1, max_length=40)
    description: str = Field(max_length=255)
    read_only: Optional[bool] = False

    validate_name = field_validator('name')(
        Validator.special_characters_validate
    )

    validate_description = field_validator('description')(
        Validator.special_characters_validate
    )


class AttachVolume(BaseModel):
    """Schema for attaching a volume to a virtual machine.

    Attributes:
        vm_id (UUID): The ID of the virtual machine.
        target (Optional[str]): The target device path for the attachment.
    """

    vm_id: UUID
    target: Optional[Path] = Field(default=None, min_length=1)

    validate_target = field_validator('target')(
        lambda v: Validator.special_characters_validate(v, allow_slash=True)
    )


class DetachVolume(BaseModel):
    """Schema for detaching a volume from a virtual machine.

    Attributes:
        vm_id (UUID): The ID of the virtual machine.
    """

    vm_id: UUID


class AttachVolumeInfo(BaseModel):
    """Schema for returning information about an attached volume.

    Attributes:
        path (Optional[str]): The path of the volume.
        size (int): The size of the volume in bytes.
        provisioning (str): The provisioning method of the volume.
    """

    path: Optional[Path] = None
    size: int
    provisioning: str
