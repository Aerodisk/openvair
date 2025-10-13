"""Module for defining the storage factory model.

This module contains abstract and concrete implementations of a factory class
that is responsible for creating storage objects based on provided
configuration data.

Classes:
    AbstractStorageFactory: Abstract base class for creating storage objects.
    StorageFactory: Concrete implementation of AbstractStorageFactory that
        creates specific storage objects.
"""

import abc
from typing import ClassVar, cast

from openvair.modules.storage.domain.base import BaseStorage
from openvair.modules.storage.domain.remotefs import nfs
from openvair.modules.storage.domain.physical_fs import localfs


class AbstractStorageFactory(metaclass=abc.ABCMeta):
    """Abstract factory for creating BaseStorage objects.

    This class provides an interface for generating storage objects based on
    provided data. It must be implemented by a subclass.

    Methods:
        get_storage: Abstract method to be implemented for returning a storage
            object.
    """

    def __call__(self, db_storage: dict) -> BaseStorage:
        """Create and return a storage object using the provided storage data.

        Args:
            db_storage (Dict): Data about the storage to be created.

        Returns:
            BaseStorage: The created storage object.
        """
        return self.get_storage(db_storage)

    @abc.abstractmethod
    def get_storage(self, db_storage: dict) -> BaseStorage:
        """Return a storage object based on provided storage data.

        Args:
            db_storage (Dict): Data about the storage to be created.

        Returns:
            BaseStorage: The created storage object.
        """
        ...


class StorageFactory(AbstractStorageFactory):
    """Concrete factory for creating BaseStorage objects.

    This class implements the AbstractStorageFactory interface, providing
    specific methods to create various types of storage objects.

    Attributes:
        _storage_classes (ClassVar): A dictionary mapping storage types to their
            corresponding classes.
    """

    _storage_classes: ClassVar = {
        'nfs': nfs.NfsStorage,
        'localfs': localfs.LocalDiskStorage,
        'local_partition': localfs.LocalPartition,
    }

    def get_storage(self, db_storage: dict) -> BaseStorage:
        """Return a storage object based on provided storage data.

        Args:
            db_storage (Dict): Data about the storage to be created.

        Returns:
            BaseStorage: The created storage object.

        Raises:
            KeyError: If the storage type is not found in _storage_classes.
        """
        storage_class = self._storage_classes[db_storage['storage_type']]
        return cast('BaseStorage', storage_class(**db_storage))
