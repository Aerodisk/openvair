# noqa: D100
from uuid import UUID
from typing import List, Optional

from pydantic import BaseModel, field_validator

from openvair.modules.tools import validators


class Attachment(BaseModel):  # noqa: D101
    id: int
    vm_id: str
    target: Optional[str] = None


class Image(BaseModel):  # noqa: D101
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


class AttachImage(BaseModel):  # noqa: D101
    vm_id: str
    target: Optional[str] = None

    @field_validator('vm_id', mode="before")
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


class DetachImage(BaseModel):  # noqa: D101
    vm_id: str

    @field_validator('vm_id', mode="before")
    @classmethod
    def _normalize_id(cls, value: str) -> str:
        return validators.uuid_validate(value)


class AttachImageInfo(BaseModel):  # noqa: D101
    path: str
    size: int
    provisioning: Optional[str] = None
