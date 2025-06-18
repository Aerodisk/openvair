"""QCOW2 template domain logic.

This module provides the concrete implementation of the `BaseTemplate` for
QCOW2 disk images. It uses `qemu-img` operations to manage template files.
"""

from typing import Any, Dict, List, Optional
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

    def __init__(  # noqa: PLR0913
        self,
        tmp_format: str,
        name: str,
        path: Path,
        related_volumes: Optional[List],
        description: Optional[str],
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
            description,
            is_backing=is_backing,
        )
        self.tmp_format: str = 'qcow2'

    def create(self, creation_data: Dict) -> Dict[str, Any]:
        """Create a QCOW2 template file from an existing volume.

        Args:
            creation_data (Dict): Must contain 'source_disk_path' (str or Path).

        Raises:
            FileNotFoundError: If the source disk does not exist.
            FileExistsError: If the target template path already exists.
            TemplateFileCreatingException: If creation via qemu-img fails.
        """
        LOG.info(f'Start creating new template: {self.name}')

        create_command = CreateTemplateDomainCommandDTO.model_validate(
            creation_data
        )

        source_disk_path = create_command.source_disk_path
        if not Path(source_disk_path).exists():
            message = f'Source disk not found: {source_disk_path}'
            raise FileNotFoundError(message)

        if self.path.exists():
            message = f'Template file already exists at {self.path}'
            raise FileExistsError(message)

        try:
            self.qemu_img_adapter.create_copy(source_disk_path, self.path)
        except QemuImgError as err:
            LOG.error(
                f'Error while creating template file: {self.path} '
                f'from {source_disk_path}'
            )
            raise TemplateFileCreatingException(str(self.path)) from err

        LOG.info(f'Template {self.name} successfull created')
        return self._to_json_dict()

    def edit(self, editing_data: Dict) -> Dict[str, Any]:
        """Rename the template file if not used as a backing image.

        Args:
            editing_data (Dict): Must contain 'new_name' (str).

        Raises:
            RuntimeError: If template is in use as a backing image.
            TemplateFileEditingException: If file renaming fails.
        """
        LOG.info(f'Start editing template: {self.name}')

        dto = EditTemplateDomainCommandDTO.model_validate(editing_data)
        if dto.name is not None:
            self._edit_name(dto.name)

        if dto.description is not None:
            LOG.info('Changing description')
            self.description = dto.description

        LOG.info('Template successfull edited')
        return self._to_json_dict()

    def delete(self) -> None:
        """Delete the QCOW2 template file.

        Raises:
            TemplateFileDeletingException: If deletion fails.
        """
        LOG.info(f'Start deleting template: {self.name}')

        try:
            self.path.unlink()
        except OSError as err:
            message = f'Failed to delete template file: {err}'
            raise TemplateFileDeletingException(message) from err

        LOG.info(f'Template {self.name} successfull deleted')

    def ensure_not_in_use(self) -> None:
        """Check the template not in use by volumes"""
        LOG.info(f'Checking template {self.name} for related volumes')

        if self.is_backing and self.related_volumes:
            message = (
                'Cannot delete or edit template name in use by volumes: '
                f'{" ".join(self.related_volumes)}'
            )
            LOG.error(message)
            raise TemplateFileEditingException(message)

        LOG.info(f'Template {self.name} have not related volumes.')

    def _edit_name(self, new_name: str) -> None:
        LOG.info(f'Changing name of template "{self.name}" to "{new_name}"')

        new_path = Path(self.path.parent.absolute() / f'template-{new_name}')
        try:
            self.path.rename(new_path)
            self.name = new_name
            self.path = new_path
            LOG.info(
                f'Name changed successfull.\n'
                f'New name: {new_name}. New path: {new_path}'
            )
        except OSError as err:
            LOG.error(f'Error while editing template file: {self.name}')
            message = f'{self.name}. Error: f{err}'
            raise TemplateFileEditingException(message) from err

        LOG.info('Templaed name susccessfull edited.')
