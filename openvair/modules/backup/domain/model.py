"""Factory for creating BaseBackuper objects.

This module includes an abstract base class `AbstractBackuperFactory`
which defines the backuper for creating BaseBackuper objects,
and a concrete implementation `BackuperFactory` which creates instances
of specific backuper types based on input data.

Classes:
    AbstractBackuperFactory: Abstract base class for creating
        BaseBackuper objects.
    BackuperFactory: Concrete implementation of AbstractBackuperFactory.
"""

from abc import ABCMeta, abstractmethod
from typing import Dict

from openvair.modules.backup.domain.base import BaseBackuper


class AbstractBackuperFactory(metaclass=ABCMeta):
    """Abstract factory for creating BaseBackuper objects."""

    def __call__(self, backuper_data: Dict) -> BaseBackuper:
        """Create an backuper by calling the factory instance.

        Args:
            backuper_data (Dict): A dictionary with the backuper data.

        Returns:
            BaseBackuper: An instance of BaseBackuper created
                using the provided data.
        """
        return self.get_backuper(backuper_data)

    @abstractmethod
    def get_backuper(self, backuper_data: Dict) -> BaseBackuper:
        """Create a BaseBackuper object from the provided data.

        Args:
            backuper_data (Dict): A dictionary with the backuper data.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.

        Returns:
            BaseBackuper: An instance of BaseBackuper.
        """
        raise NotImplementedError
