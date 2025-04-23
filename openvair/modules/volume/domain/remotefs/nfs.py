"""Module for managing NFS volumes.

This module provides classes and methods for creating, deleting, and managing
NFS volumes in a virtualized environment.

Classes:
    NfsVolume: Class for managing NFS volumes.
"""

from typing import Any, Dict
from pathlib import Path

from openvair.libs.log import get_logger
from openvair.libs.cli.models import ExecuteParams
from openvair.libs.cli.executor import execute
from openvair.libs.cli.exceptions import ExecuteError
from openvair.libs.qemu_img.adapter import QemuImgAdapter
from openvair.modules.volume.domain.base import BaseVolume
from openvair.modules.volume.domain.remotefs import exceptions
from openvair.modules.volume.adapters.dto.internal.commands import (
    CreateVolumeFromTemplateDomainCommandDTO,
)

LOG = get_logger(__name__)


class NfsVolume(BaseVolume):
    """Class for managing NFS volumes.

    This class provides methods for creating, deleting, extending, and
    retrieving information about NFS volumes.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize an instance of the NfsVolume class.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        LOG.info('Initialized NfsVolume')
        super(NfsVolume, self).__init__(*args, **kwargs)
        self._execute_as_root = False
        self.provisioning = 'metadata'

    def create(self) -> Dict:
        """Create a new NFS volume.

        Raises:
            QemuImgCreateException: If there's an error while creating
                the volume.

        Returns:
            Dict: A dictionary representation of the volume's attributes.
        """
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
            message = f'Qemu img create raised exception: {err!s}'
            LOG.error(message)
            raise exceptions.QemuImgCreateException(message)

        LOG.info(f'Created volume {volume_path}')
        return self.__dict__

    def delete(self) -> Dict:
        """Delete an existing NFS volume.

        Raises:
            DeleteVolumeException: If there's an error while deleting
                the volume.

        Returns:
            Dict: A dictionary representation of the volume's attributes.
        """
        volume_path = Path(self.path, f'volume-{self.id}')
        try:
            execute(
                'rm',
                '-f',
                str(volume_path),
                params=ExecuteParams(  # noqa: S604
                    run_as_root=self._execute_as_root,
                    shell=True,
                    raise_on_error=True,
                ),
            )
        except (ExecuteError, OSError) as err:
            message = f'Delete volume raised exception: {err!s}'
            LOG.error(message)
            raise exceptions.DeleteVolumeException(message)

        LOG.info(f'Deleted volume {volume_path}')
        return self.__dict__

    def extend(self, new_size: str) -> Dict:
        """Extend the size of an existing NFS volume.

        Args:
            new_size (str): The new size of the volume.

        Raises:
            QemuImgExtendException: If there's an error while extending
                the volume.

        Returns:
            Dict: A dictionary representation of the volume's attributes.
        """
        self._check_volume_exists()
        volume_path = Path(self.path, f'volume-{self.id}')
        try:
            execute(
                'qemu-img',
                'resize',
                str(volume_path),
                str(new_size),
                params=ExecuteParams(  # noqa: S604
                    shell=True,
                    run_as_root=self._execute_as_root,
                ),
            )
        except (ExecuteError, OSError) as err:
            message = f'Qemu img extend volume raised exception: {err!s}'
            LOG.error(message)
            raise exceptions.QemuImgExtendException(message)

        LOG.info(f'Extended volume {volume_path} to size {new_size}')
        return self.__dict__

    def attach_volume_info(self) -> Dict:
        """Get information about the NFS volume.

        Returns:
            Dict: A dictionary containing information about the volume.
        """
        self._check_volume_exists()
        qemu_volume_info = self._get_info_about_volume()
        LOG.info(f'Attached info about volume {self.id}')
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
