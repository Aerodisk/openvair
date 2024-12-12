"""Factory module for creating BaseBackuper objects.

This module defines an abstract base class `AbstractBackuperFactory` for
creating BaseBackuper objects, and a concrete implementation
`BackuperFactory` that creates instances of specific backuper types based
on input data.

Classes:
    AbstractBackuperFactory: Defines the interface for backuper factories.
    BackuperFactory: A factory that creates specific BaseBackuper instances.
"""

from abc import ABCMeta, abstractmethod
from typing import Dict, Type, ClassVar

from openvair.modules.backup.domain.base import DBBackuper, BaseBackuper
from openvair.libs.messaging.messaging_agents import MessagingClient
from openvair.modules.backup.domain.fs_backup.restic_backuper import (
    ResticBackuper,
)


class AbstractBackuperFactory(metaclass=ABCMeta):
    """Abstract factory for creating BaseBackuper objects.

    This class serves as a blueprint for factories that create instances
    of BaseBackuper. Subclasses must implement the `get_backuper` method.

    Methods:
        __call__: Creates a backuper by invoking the factory instance.
        get_backuper: Abstract method to create a BaseBackuper object.
    """

    def __call__(self, backuper_data: Dict) -> BaseBackuper:
        """Create a backuper by calling the factory instance.

        Args:
            backuper_data (Dict): A dictionary containing backuper configuration
                and type information.

        Returns:
            BaseBackuper: An instance of BaseBackuper corresponding to the
                specified type.
        """
        backuper_type = backuper_data.pop('backuper_type')
        return self.get_backuper(backuper_type, backuper_data)

    @abstractmethod
    def get_backuper(
        self, backuper_type: str, backuper_data: Dict
    ) -> BaseBackuper:
        """Create a BaseBackuper object from the provided data.

        Args:
            backuper_type (str): The type of backuper to create.
            backuper_data (Dict): A dictionary containing backuper-specific
                data.

        Raises:
            NotImplementedError: Must be implemented by subclasses.

        Returns:
            BaseBackuper: An instance of BaseBackuper corresponding to the type.
        """
        raise NotImplementedError


class BackuperFactory(AbstractBackuperFactory):
    """Concrete factory for creating BaseBackuper objects.

    This class maps backuper types to their corresponding classes and
    instantiates the appropriate backuper based on input data.

    Attributes:
        _backuper_classes (ClassVar[Dict[str, Type[BaseBackuper]]]): A mapping
            of backuper types to their corresponding classes.
    """

    _backuper_classes: ClassVar = {
        'postgres': DBBackuper,
        'restic': ResticBackuper,
    }

    def get_backuper(
        self, backuper_type: str, backuper_data: Dict
    ) -> BaseBackuper:
        """Create a BaseBackuper object from the provided data.

        Args:
            backuper_type (str): The type of backuper to create
                (e.g., "postgres").
            backuper_data (Dict): A dictionary containing backuper-specific
                data.

        Raises:
            KeyError: If the backuper_type is not recognized.

        Returns:
            BaseBackuper: An instance of the requested BaseBackuper type.
        """
        backuper_cls: Type[BaseBackuper] = self._backuper_classes[backuper_type]
        return backuper_cls(**backuper_data)


if __name__ == '__main__':
    domain_rpc = MessagingClient(queue_name='backup_service_layer_domain')
    domain_rpc.call(
        method_name=ResticBackuper.new_method.__name__,
        data_for_manager={'backuper_type': 'restic'},
        data_for_method={},
    )
