"""Module for managing virtual network models and their creation.

This module defines abstract and concrete factory classes for creating
virtual network instances based on their type.

Classes:
    - AbstractVirtualNetworkFactory: Abstract factory for creating virtual
        network instances.
    - VirtualNetworkFactory: Concrete factory for creating virtual network
        instances.
"""

import abc
from typing import ClassVar, cast

from openvair.modules.virtual_network.domain.base import BaseVirtualNetwork
from openvair.modules.virtual_network.domain.bridge_network.bridge_net import (
    BridgeNetwork,
)


class AbstractVirtualNetworkFactory(metaclass=abc.ABCMeta):
    """Abstract factory for creating objects of the BaseVirtualNetwork class."""

    def __call__(self, virtual_network_data: dict) -> BaseVirtualNetwork:
        """Creates and returns a virtual network instance.

        This method is called when an instance of the factory is used as a
        callable. It delegates the creation of the virtual network instance to
        the `get_interface` method.

        Args:
            virtual_network_data (Dict): Dictionary with virtual network data.

        Returns:
            BaseVirtualNetwork: An instance of a class derived from
            BaseVirtualNetwork.
        """
        return self.get_interface(virtual_network_data)

    @abc.abstractmethod
    def get_interface(self, virtual_network_data: dict) -> BaseVirtualNetwork:
        """Takes virtual network data and returns a BaseVirtualNetwork object.

        Args:
            virtual_network_data: Dictionary with virtual network data.

        Returns:
            Object of the BaseVirtualNetwork class.
        """
        ...


class VirtualNetworkFactory(AbstractVirtualNetworkFactory):
    """Factory for creating objects of the BaseVirtualNetwork class."""

    _virtual_network_classes: ClassVar = {'bridge': BridgeNetwork}

    def get_interface(self, virtual_network_data: dict) -> BaseVirtualNetwork:
        """Takes virtual network data and returns a BaseVirtualNetwork object.

        Args:
            virtual_network_data: Dictionary with virtual network data.

        Returns:
            Object of the BaseVirtualNetwork class.
        """
        virtual_network_class = self._virtual_network_classes[
            virtual_network_data['forward_mode']
        ]
        return cast(
            'BaseVirtualNetwork', virtual_network_class(**virtual_network_data)
        )
