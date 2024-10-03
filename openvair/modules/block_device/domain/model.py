"""Factory for creating BaseBlockInterface objects.

This module includes an abstract base class `AbstractInterfaceFactory`
which defines the interface for creating BaseBlockInterface objects,
and a concrete implementation `InterfaceFactory` which creates instances
of specific block interface types based on input data.

Classes:
    AbstractInterfaceFactory: Abstract base class for creating
        BaseBlockInterface objects.
    InterfaceFactory: Concrete implementation of AbstractInterfaceFactory.
"""

import abc
from typing import Dict, ClassVar

from openvair.modules.block_device.domain.base import BaseBlockInterface
from openvair.modules.block_device.domain.iscsi import iscsi
from openvair.modules.block_device.domain.fibre_channel import fibre_channel


class AbstractInterfaceFactory(metaclass=abc.ABCMeta):
    """Abstract factory for creating BaseBlockInterface objects."""

    def __call__(self, interface_data: Dict):
        """Create an interface by calling the factory instance.

        Args:
            interface_data (Dict): A dictionary with the interface data.

        Returns:
            BaseBlockInterface: An instance of BaseBlockInterface created
                using the provided data.
        """
        return self.get_interface(interface_data)

    @abc.abstractmethod
    def get_interface(self, interface_data: Dict) -> BaseBlockInterface:
        """Create a BaseBlockInterface object from the provided data.

        Args:
            interface_data (Dict): A dictionary with the interface data.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.

        Returns:
            BaseBlockInterface: An instance of BaseBlockInterface.
        """
        raise NotImplementedError


class InterfaceFactory(AbstractInterfaceFactory):
    """Factory for creating BaseBlockInterface objects."""

    _interface_classes: ClassVar = {
        'iscsi': iscsi.ISCSIInterface,
        'fibre_channel': fibre_channel.FibreChannelInterface,
    }

    def get_interface(self, interface_data: Dict) -> BaseBlockInterface:
        """Create a BaseBlockInterface object using provided interface data.

        Args:
            interface_data (Dict): A dictionary with the interface data.

        Returns:
            BaseBlockInterface: An instance of BaseBlockInterface.

        Raises:
            KeyError: If the corresponding interface type is not found.
        """
        interface_class = self._interface_classes[interface_data['inf_type']]
        return interface_class(**interface_data)
