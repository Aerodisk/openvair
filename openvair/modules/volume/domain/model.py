"""Module for the volume domain model.

This module defines factories for creating volume objects based on different
storage types. The factories are responsible for initializing volume objects
using the data provided from the database.

Classes:
    AbstractVolumeFactory: Abstract factory for creating BaseVolume objects.
    VolumeFactory: Concrete factory for creating BaseVolume objects based on
        storage type.
"""

import abc
from typing import Any, Mapping, ClassVar

from typing_extensions import TypeAlias

from openvair.modules.volume.domain.base import BaseVolume
from openvair.modules.volume.domain.remotefs import nfs
from openvair.modules.volume.domain.physical_fs import localfs

VolumeCls: TypeAlias = type[nfs.NfsVolume] | type[localfs.LocalFSVolume]


class AbstractVolumeFactory(metaclass=abc.ABCMeta):
    """Abstract factory for creating BaseVolume objects."""

    def __call__(self, db_volume: Mapping[str, Any]) -> BaseVolume:
        """Create a volume instance based on the provided database data.

        Args:
            db_volume (Dict): A dictionary containing data from the database
                about the volume.

        Returns:
            BaseVolume: An instance of a BaseVolume subclass.
        """
        return self.get_volume(db_volume)

    @abc.abstractmethod
    def get_volume(self, db_volume: Mapping[str, Any]) -> BaseVolume:
        """Retrieve a BaseVolume instance based on the database data.

        Args:
            db_volume (Dict): A dictionary containing data about the volume.

        Returns:
            BaseVolume: An instance of a BaseVolume subclass.

        Raises:
            NotImplementedError: Must be implemented by subclasses.
        """
        ...


class VolumeFactory(AbstractVolumeFactory):
    """Factory for creating BaseVolume objects based on storage type.

    This factory determines the appropriate volume class to instantiate based
    on the storage type specified in the database data.
    """

    _volume_classes: ClassVar[dict[str, VolumeCls]] = {
        'nfs': nfs.NfsVolume,
        'localfs': localfs.LocalFSVolume,
    }

    def get_volume(self, db_volume: Mapping[str, Any]) -> BaseVolume:
        """Retrieve a BaseVolume instance based on the storage type.

        Args:
            db_volume (Dict): A dictionary containing data about the volume.

        Returns:
            BaseVolume: An instance of a BaseVolume subclass.

        Raises:
            KeyError: If the storage type is not found in the factory's
                mappings.
        """
        storage_type = db_volume['storage_type']
        volume_class = self._volume_classes[storage_type]
        return volume_class(**db_volume)
