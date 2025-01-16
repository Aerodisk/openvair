"""Pydantic schemas for the Image entrypoints.

This module defines the data models used for validating and serializing
image-related requests and responses in the API layer. These schemas
ensure the consistency and correctness of data structures for operations
like attaching, detaching, and retrieving image metadata.

Classes:
    Attachment: Represents an attachment of an image to a virtual machine.
    Image: Represents metadata of an image, including its attributes and
        associated attachments.
    AttachImage: Represents the data required to attach an image to a VM.
    DetachImage: Represents the data required to detach an image from a VM.
    AttachImageInfo: Represents metadata for an attached image, such as
        its path, size, and provisioning information.
"""

from uuid import UUID
from typing import List, Optional

from pydantic import BaseModel, field_validator

from openvair.modules.tools import validators


class Attachment(BaseModel):
    """Represents an attachment of an image to a virtual machine.

    This schema defines the structure for an image attachment, including
    the ID of the attachment, the VM it is attached to, and the target
    path, if applicable.

    Attributes:
        id (int): The ID of the attachment.
        vm_id (str): The ID of the virtual machine to which the image is
            attached.
        target (Optional[str]): The target path for the attachment.
    """

    id: int
    vm_id: str
    target: Optional[str] = None


class Image(BaseModel):
    """Represents metadata of an image.

    This schema includes details about an image, such as its name, size,
    storage location, and associated attachments.

    Attributes:
        id (UUID): The unique identifier of the image.
        name (str): The name of the image.
        size (Optional[int]): The size of the image in bytes.
        path (str): The file path of the image.
        status (str): The current status of the image (e.g., active, inactive).
        information (Optional[str]): Additional information about the image.
        description (Optional[str]): A description of the image.
        storage_id (UUID): The ID of the storage where the image is located.
        user_id (Optional[str]): The ID of the user who owns the image.
        attachments (List[Attachment]): A list of attachments for this image.
    """

    id: UUID
    name: str
    size: Optional[int] = None
    path: str
    status: str
    information: Optional[str] = None
    description: Optional[str] = None
    storage_id: UUID
    user_id: Optional[str] = None
    attachments: List[Attachment] = []


class AttachImage(BaseModel):
    """Represents the data required to attach an image to a virtual machine.

    This schema validates the data provided for attaching an image to a VM,
    including the VM ID and an optional target path.

    Attributes:
        vm_id (str): The ID of the virtual machine to which the image will be
            attached.
        target (Optional[str]): The optional target path for the attachment.

    Methods:
        _normalize_id: Validates and normalizes the VM ID.
        path_validator: Validates the target path, ensuring it meets required
        conditions (e.g., length, special character validation).
    """

    vm_id: str
    target: Optional[str] = None

    @field_validator('vm_id', mode='before')
    @classmethod
    def _normalize_id(cls, value: str) -> str:
        return validators.uuid_validate(value)

    @field_validator('target')
    @classmethod
    def path_validator(cls, value: str) -> str:  # noqa: D102
        if len(value) < 1:
            message = 'Length of target must be bigger then 0.'
            raise ValueError(message)
        validators.special_characters_path_validate(value)
        return value


class DetachImage(BaseModel):
    """Represents the data required to detach an image from a virtual machine.

    This schema validates the data provided for detaching an image from a VM.

    Attributes:
        vm_id (str): The ID of the virtual machine from which the image will be
            detached.

    Methods:
        _normalize_id: Validates and normalizes the VM ID.
    """

    vm_id: str

    @field_validator('vm_id', mode='before')
    @classmethod
    def _normalize_id(cls, value: str) -> str:
        return validators.uuid_validate(value)


class AttachImageInfo(BaseModel):
    """Represents metadata for an attached image.

    This schema includes information about an attached image, such as its
    file path, size, and provisioning details.

    Attributes:
        path (str): The file path of the attached image.
        size (int): The size of the attached image in bytes.
        provisioning (Optional[str]): The provisioning type or details
        for the attached image.
    """

    path: str
    size: int
    provisioning: Optional[str] = None
