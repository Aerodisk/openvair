"""QCOW2 template domain logic.

This module provides the concrete implementation of the `BaseTemplate` for
QCOW2 disk images. It uses `qemu-img` operations to manage template files.
"""

from typing import Dict, List, Optional
from pathlib import Path

from openvair.libs.log import get_logger
from openvair.libs.qemu_img.exceptions import QemuImgError
from openvair.modules.template.domain.base import BaseTemplate
from openvair.modules.template.domain.exception import (
    TemplateFileEditingException,
    TemplateFileCreatingException,
    TemplateFileDeletingException,
)
from openvair.modules.template.adapters.dto.internal.commands import (
    EditTemplateDomainCommandDTO,
    CreateTemplateDomainCommandDTO,
)

LOG = get_logger(__name__)


class Qcow2Template(BaseTemplate):
    """Concrete implementation of `BaseTemplate` for QCOW2 images.

    Provides logic for creating, editing, and deleting template files in
    `qcow2` format using the `qemu-img` utility.
    """

    def __init__(
        self,
        tmp_format: str,
        name: str,
        path: Path,
        related_volumes: Optional[List],
        *,
        is_backing: bool,
    ) -> None:
        """Initialize a QCOW2 template instance.

        Inherits base fields and logic from `BaseTemplate`.
        """
        super().__init__(
            tmp_format,
            name,
            path,
            related_volumes,
            is_backing=is_backing,
        )
        self.format: str = 'qcow2'

    def create(self, creation_data: Dict) -> None:
        """Create a QCOW2 template file from an existing volume.

        Args:
            creation_data (Dict): Must contain 'source_disk_path' (str or Path).

        Raises:
            FileNotFoundError: If the source disk does not exist.
            FileExistsError: If the target template path already exists.
            TemplateFileCreatingException: If creation via qemu-img fails.
        """
        dto = CreateTemplateDomainCommandDTO.model_validate(creation_data)
        source_disk_path = dto.source_disk_path

        if not Path(source_disk_path).exists():
            message = f'Source disk not found: {source_disk_path}'
            raise FileNotFoundError(message)

        if self.path.exists():
            message = f'Template already exists at {self.path}'
            raise FileExistsError(message)

        try:
            self.qemu_img_adapter.create_copy(source_disk_path, self.path)
        except QemuImgError as err:
            LOG.error(
                f'Error while creating template file: {self.path} '
                f'from {source_disk_path}'
            )
            raise TemplateFileCreatingException(str(self.path)) from err

    def edit(self, editing_data: Dict) -> None:
        """Rename the template file if not used as a backing image.

        Args:
            editing_data (Dict): Must contain 'new_name' (str).

        Raises:
            RuntimeError: If template is in use as a backing image.
            TemplateFileEditingException: If file renaming fails.
        """
        if self.is_backing and self.related_volumes:
            message = 'Cannot edit template in use'
            raise TemplateFileEditingException(message)
        dto: EditTemplateDomainCommandDTO = (
            EditTemplateDomainCommandDTO.model_validate(editing_data)
        )
        new_name = dto.name
        new_path = self.path.parent.absolute() / new_name
        try:
            self.path.rename(new_path)
            self.name = new_name
            self.path = new_path
        except OSError as err:
            LOG.error(f'Error while editing template file: {self.name}')
            raise TemplateFileEditingException(str(self.name)) from err

    def delete(self) -> None:
        """Delete the QCOW2 template file.

        Raises:
            TemplateFileDeletingException: If deletion fails.
        """
        try:
            self.path.unlink()
        except OSError as err:
            message = f'Failed to delete template file: {err}'
            raise TemplateFileDeletingException(message) from err
