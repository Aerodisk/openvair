"""Module for managing local filesystem volumes.

This module provides classes and methods for creating, deleting, and managing
local filesystem volumes in a virtualized environment.

Classes:
    BaseLocalFSVolume: Base class for local filesystem volumes.
    LocalFSVolume: Class for managing local filesystem volumes.
"""

from typing import Any, Dict
from pathlib import Path

from openvair.libs.log import get_logger
from openvair.libs.cli.models import ExecuteParams
from openvair.libs.cli.executor import execute
from openvair.libs.cli.exceptions import ExecuteError
from openvair.libs.qemu_img.adapter import QemuImgAdapter
from openvair.modules.volume.domain.base import BaseVolume
from openvair.modules.volume.adapters.dto.internal.commands import (
    # CreateVolumeCloneServiceCommandDTO,
    CreateVolumeFromTemplateDomainCommandDTO,
)

LOG = get_logger(__name__)


class LocalFSVolume(BaseVolume):
    """Class for managing local filesystem volumes.

    This class provides methods for creating, deleting, and managing local
    filesystem volumes.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize a LocalFSVolume instance."""
        super().__init__(*args, **kwargs)
        self._execute_as_root = False
        self.provisioning = 'metadata'

    def create(self) -> Dict:
        """Create a new volume.

        Returns:
            Dict: A dictionary representation of the volume's attributes.
        """
        LOG.info(
            f'Creating volume with id={self.id}, path={self.path},'
            f'size={self.size}, format={self.format}'
        )
        preallocation = self.provisioning if self.format != 'raw' else 'off'
        volume_path = Path(self.path, f'volume-{self.id}')
        try:
            execute(
                'qemu-img',
                'create',
                '-f',
                self.format,
                '-o',
                f'preallocation={preallocation}',
                str(volume_path),
                str(self.size),
                params=ExecuteParams(  # noqa: S604
                    run_as_root=self._execute_as_root,
                    shell=True,
                    raise_on_error=True,
                ),
            )
        except (ExecuteError, OSError) as err:
            LOG.error(f'Error while creating volume: {err!s}')
            raise
        return self.__dict__

    def delete(self) -> Dict:
        """Delete an existing volume.

        Returns:
            Dict: A dictionary representation of the volume's attributes.
        """
        LOG.info(f'Deleting volume with id={self.id}, path={self.path}')
        volume_path = Path(self.path, f'volume-{self.id}')
        try:
            execute(
                'rm',
                '-f',
                str(volume_path),
                params=ExecuteParams(  # noqa: S604
                    run_as_root=True,
                    shell=True,
                    raise_on_error=True,
                ),
            )
        except (ExecuteError, OSError) as err:
            LOG.error(f'Error while deleting volume: {err!s}')
            raise

        return self.__dict__

    def extend(self, new_size: str) -> Dict:
        """Extend an existing volume to the given size.

        Args:
            new_size (str): The new size for the volume.

        Returns:
            Dict: A dictionary representation of the volume's attributes.
        """
        LOG.info(
            f'Extending volume with id={self.id},'
            f'path={self.path} to new size={new_size}'
        )
        self._check_volume_exists()
        volume_path = Path(self.path, f'volume-{self.id}')
        try:
            execute(
                'qemu-img',
                'resize',
                str(volume_path),
                str(new_size),
                params=ExecuteParams(  # noqa: S604
                    run_as_root=self._execute_as_root,
                    shell=True,
                    raise_on_error=True,
                ),
            )
        except (ExecuteError, OSError) as err:
            LOG.error(f'Error while extending volume: {err!s}')
            raise

        return self.__dict__

    def clone (self, data: Dict) -> Dict:
        """Clone an existing volume.

        Args:
            data (Dict): A dictionary containing the necessary data for cloning.

        Returns:
            Dict: A dictionary representation of the cloned volume's attributes.
        """
        LOG.info(
            f'Cloning volume with id={self.id}, path={self.path},'
            f'size={self.size}, format={self.format}'
        )
        qemu_img_adapter = QemuImgAdapter()
        source_path = data.get['source_path']
        LOG.info(f'Source path for cloning: {source_path}')

        if not source_path or not Path(source_path).exists():
            msg = 'Source_path is required and must exist'
            LOG.error(msg)
            raise ValueError(msg)

        target_path = Path(self.path, f'volume-{self.id}')
        LOG.info(f'Target path for cloning: {target_path}')

        LOG.info('Starting cloning process using qemu-img adapter...')
        qemu_img_adapter.create_copy(
            Path(source_path),
            target_path,
            fmt=self.format,
        )
        return self.__dict__

    def attach_volume_info(self) -> Dict:
        """Get information about an existing volume.

        Returns:
            Dict: A dictionary containing information about the volume.
        """
        LOG.info(f'Getting info for volume with id={self.id}, path={self.path}')
        self._check_volume_exists()
        qemu_volume_info = self._get_info_about_volume()
        return {
            'path': f'{self.path}/volume-{self.id}',
            'size': qemu_volume_info.get('virtual-size', self.size),
            'used': qemu_volume_info.get('actual-size', 0),
            'provisioning': self.provisioning,
        }

    def create_from_template(self, data: Dict) -> Dict:  # noqa: D102
        qemu_img_adapter = QemuImgAdapter()
        creation_data = CreateVolumeFromTemplateDomainCommandDTO.model_validate(
            data
        )

        if creation_data.is_backing:
            qemu_img_adapter.create_backing_volume(
                creation_data.template_path,
                Path(f'{self.path}/volume-{self.id}'),
            )
        else:
            qemu_img_adapter.create_copy(
                creation_data.template_path,
                Path(f'{self.path}/volume-{self.id}'),
            )
        return self.__dict__
