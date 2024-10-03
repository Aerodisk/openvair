# noqa: D100
from uuid import UUID
from typing import List, Optional

from pydantic import BaseModel, validator

from openvair.modules.tools import validators


class Attachment(BaseModel):  # noqa: D101
    id: int
    vm_id: str
    target: Optional[str]


class Image(BaseModel):  # noqa: D101
    id: UUID
    name: str
    size: Optional[int]
    path: str
    status: str
    information: Optional[str]
    description: Optional[str]
    storage_id: UUID
    user_id: Optional[str]
    attachments: List[Attachment] = []


class AttachImage(BaseModel):  # noqa: D101
    vm_id: str
    target: Optional[str]

    @classmethod
    @validator('vm_id', pre=True)
    def _normalize_id(cls, value: str) -> str:
        return validators.uuid_validate(value)

    @classmethod
    @validator('target')
    def path_validator(cls, value: str) -> str:  # noqa: D102
        if len(value) < 1:
            message = 'Length of target must be bigger then 0.'
            raise ValueError(message)
        validators.special_characters_path_validate(value)
        return value


class DetachImage(BaseModel):  # noqa: D101
    vm_id: str

    @classmethod
    @validator('vm_id', pre=True)
    def _normalize_id(cls, value: str) -> str:
        return validators.uuid_validate(value)


class AttachImageInfo(BaseModel):  # noqa: D101
    path: str
    size: int
    provisioning: Optional[str]
