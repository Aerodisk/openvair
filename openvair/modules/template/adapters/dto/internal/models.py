"""DTOs for internal data structures in the template module.

Includes models used between ORM and domain/service layers.
"""

from uuid import UUID
from typing import List, Literal, Optional
from pathlib import Path
from datetime import datetime

from openvair.common.base_pydantic_models import BaseDTOModel
from openvair.modules.template.shared.enums import TemplateStatus


class ApiTemplateModelDTO(BaseDTOModel):
    """DTO used to represent a template in the API layer.

    Attributes:
        id (UUID): Unique ID of the template.
        name (str): Name of the template.
        description (Optional[str]): Optional description.
        path (Path): Filesystem path to the template image.
        tmp_format (str): Disk format (e.g., qcow2, raw).
        size (int): Size of the template in bytes.
        status (TemplateStatus): Lifecycle status of the template.
        is_backing (bool): Whether this template is used as a backing image.
        created_at (datetime): Time of creation.
        storage_id (UUID): Associated storage ID.
    """

    id: UUID
    name: str
    description: Optional[str]
    path: Path
    tmp_format: str
    size: int
    status: TemplateStatus
    is_backing: bool
    created_at: datetime
    storage_id: UUID


class DomainTemplateModelDTO(BaseDTOModel):
    """DTO for domain logic operations on templates.

    Attributes:
        tmp_format (str): Disk format of the template.
        name (str): Template name.
        path (Path): Full filesystem path to the image.
        related_volumes (Optional[List]): Volumes using this template.
        is_backing (bool): Whether this template is a backing image.
        description (str): Description of the template.
    """

    tmp_format: str
    name: str
    path: Path
    related_volumes: Optional[List] = None
    is_backing: bool
    description: str


class CreateTemplateModelDTO(BaseDTOModel):
    """DTO for creating a new template from service logic.

    Attributes:
        name (str): Name of the new template.
        description (Optional[str]): Description of the template.
        path (Path): Filesystem path for the template image.
        tmp_format (Literal['qcow2', 'raw']): Disk format.
        storage_id (UUID): Associated storage.
        is_backing (bool): Whether this is a backing image.
    """

    name: str
    description: Optional[str]
    path: Path
    tmp_format: Literal['qcow2', 'raw']
    storage_id: UUID
    is_backing: bool
