"""Base classes for volume management.

This module provides abstract base classes and utility methods for managing
volumes, both local and remote.

Classes:
    BaseVolume: Abstract base class for volume operations.
    RemoteFSVolume: Abstract base class for RemoteFS volume operations.
"""

import re
import abc
from typing import Any, Dict, cast
from pathlib import Path

from openvair.libs.log import get_logger
from openvair.libs.cli.models import ExecuteParams, ExecutionResult
from openvair.libs.cli.executor import execute
from openvair.modules.volume.domain.exceptions import (
    VolumeDoesNotExistOnStorage,
)
from openvair.libs.data_handlers.json.serializer import deserialize_json

LOG = get_logger(__name__)


class BaseVolume(metaclass=abc.ABCMeta):
    """Abstract base class for volume operations.

    This class provides an interface for common volume operations such as
    creating, deleting, and extending volumes.
    """

    def __init__(self, **kwargs: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize a BaseVolume instance.

        Args:
            **kwargs: Arbitrary keyword arguments used to set the volume
                attributes.
        """
        LOG.info('Initialized BaseVolume.')
        self.id = str(kwargs.get('id', ''))
        self.format = kwargs.get('format', 'raw')
        self.size = kwargs.get('size', 0)
        self.description = kwargs.get('description', '')
        self.storage_type = kwargs.get('storage_type', '')
        self.path = kwargs.get('path', '')

    @abc.abstractmethod
    def create(self) -> Dict:
        """Create a new volume.

        Returns:
            Dict: A dictionary representation of the volume's attributes.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def delete(self) -> Dict:
        """Delete an existing volume.

        Returns:
            Dict: A dictionary representation of the volume's attributes.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def extend(self, new_size: str) -> Dict:
        """Extend an existing volume to the given size.

        Args:
            new_size (str): The new size for the volume.

        Returns:
            Dict: A dictionary representation of the volume's attributes.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def clone(self, data: Dict) -> Dict:
        """Clone an existing volume.

        Args:
            data (Dict): A dictionary containing the necessary data for cloning.

        Returns:
            Dict: A dictionary representation of the cloned volume's attributes.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def attach_volume_info(self) -> Dict:
        """Get information about an existing volume.

        Returns:
            Dict: A dictionary containing information about the volume.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def create_from_template(self, data: Dict) -> Dict:  # noqa: D102
        raise NotImplementedError

    def _check_volume_exists(self) -> None:
        """Check if the volume exists on the storage.

        Raises:
            Exception: If the volume does not exist.
        """
        if not Path(f'{self.path}/volume-{self.id}').exists():
            raise VolumeDoesNotExistOnStorage(self.id)

    def _get_info_about_volume(self) -> Dict:
        """Get detailed information about the volume using `qemu-img`.

        Returns:
            Dict: A dictionary containing detailed information about the volume.

        Raises:
            json.JSONDecodeError: If the `qemu-img` output is not valid JSON.
        """
        volume_path = Path(self.path, f'volume-{self.id}')
        try:
            exec_result: ExecutionResult = execute(
                'qemu-img',
                'info',
                '--output=json',
                str(volume_path),
                params=ExecuteParams(  # noqa: S604
                    shell=True,
                    raise_on_error=False,
                    timeout=1,
                ),
            )

            if exec_result.returncode != 0:
                write_lock_warning_pattern = re.compile(
                    r'Failed to get shared "write" lock'
                )
                if write_lock_warning_pattern.search(exec_result.stderr or ''):
                    LOG.warning(exec_result.stderr)
                else:
                    LOG.error(
                        'Error executing `qemu-img info`: '
                        f'{exec_result.stderr or exec_result.stdout}'
                    )
                return {}

            # Если stdout пустой, смысла парсить тоже нет
            if not exec_result.stdout:
                LOG.error('`qemu-img info` returned empty output.')
                return {}

            return cast(Dict, deserialize_json(exec_result.stdout))
        except Exception as err:  # noqa: BLE001
            LOG.error(f'Unexpected error in _get_info_about_volume: {err}')
            return {}
