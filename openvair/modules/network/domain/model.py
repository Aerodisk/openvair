"""Factory classes for network domain entities.

This module defines abstract and concrete factory classes for creating
network interface objects based on provided data.

Classes:
    AbstractInterfaceFactory: Abstract factory for creating network interface
        objects.
    InterfaceFactory: Concrete factory implementation for creating network
        interface objects.
"""

import abc
from typing import Dict, Type, ClassVar

from openvair.modules.network.domain.base import BaseInterface
from openvair.modules.network.domain.bridges import netplan, ovs_bridge
from openvair.modules.network.domain.interfaces import virtual, physical


class AbstractInterfaceFactory(metaclass=abc.ABCMeta):
    """Abstract factory for creating objects of the BaseInterface class."""

    def __call__(self, interface_data: Dict) -> BaseInterface:
        """Create a BaseInterface object from the provided data.

        Args:
            interface_data (Dict): A dictionary containing interface data.

        Returns:
            BaseInterface: An object of the BaseInterface class.
        """
        return self.get_interface(interface_data)

    @abc.abstractmethod
    def get_interface(self, interface_data: Dict) -> BaseInterface:
        """Get an object of the BaseInterface class.

        Args:
            interface_data: A dictionary with interface data.

        Returns:
            An object of the BaseInterface class.
        """
        ...


class InterfaceFactory(AbstractInterfaceFactory):
    """Factory for creating objects of the BaseInterface class."""

    _interface_classes: ClassVar = {
        'physical': physical.PhysicalInterface,
        'virtual': virtual.VirtualInterface,
        'ubuntu': {
            'ovs': ovs_bridge.OVSInterface,
            'netplan': netplan.NetplanInterface,
        },
    }

    def get_interface(self, interface_data: Dict) -> BaseInterface:
        """Get an object of the BaseInterface class.

        Args:
            interface_data: A dictionary with interface data.

        Returns:
            An object of the BaseInterface class.

        Raises:
            KeyError: If the corresponding interface type is not found.
        """
        inf_type: str = interface_data['inf_type']
        interface_class: Type[BaseInterface]
        if inf_type == 'ubuntu':
            network_config_manager = interface_data['network_config_manager']
            interface_class = self._interface_classes['ubuntu'][
                network_config_manager
            ]
        else:
            interface_class = self._interface_classes[inf_type]

        return interface_class(**interface_data)
