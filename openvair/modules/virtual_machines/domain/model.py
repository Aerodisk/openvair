"""Module for virtual machine driver factory.

This module defines abstract and concrete factory classes for creating
virtual machine drivers. The factories are responsible for instantiating
the appropriate driver based on the provided virtual machine
configuration.

Classes:
    AbstractVMDriverFactory: Abstract factory class for creating VM drivers.
    VMDriverFactory: Concrete factory class for creating VM drivers based on
        the configuration.
"""

import abc
from typing import Dict, ClassVar

from openvair.modules.virtual_machines.config import VM_DRIVER
from openvair.modules.virtual_machines.domain.base import BaseVMDriver
from openvair.modules.virtual_machines.domain.libvirt2.driver import (
    LibvirtDriver,
)


class AbstractVMDriverFactory(metaclass=abc.ABCMeta):
    """Abstract factory for creating BaseVMDriver objects.

    This class defines the interface for a factory that creates virtual
    machine driver instances.
    """

    def __call__(self, db_virtual_machine: Dict) -> BaseVMDriver:
        """Create a VM driver instance.

        Args:
            db_virtual_machine (Dict): Dictionary containing the virtual
                machine configuration.

        Returns:
            BaseVMDriver: An instance of a virtual machine driver.
        """
        return self.get_vm_driver(db_virtual_machine)

    @abc.abstractmethod
    def get_vm_driver(self, db_virtual_machine: Dict) -> BaseVMDriver:
        """Create a VM driver instance based on the configuration.

        Args:
            db_virtual_machine (Dict): Dictionary containing the virtual
                machine configuration.

        Returns:
            BaseVMDriver: An instance of a virtual machine driver.
        """
        pass


class VMDriverFactory(AbstractVMDriverFactory):
    """Factory for creating BaseVMDriver objects.

    This class creates virtual machine drivers based on the configuration
    provided in the database entry.

    Attributes:
        _vm_driver_classes (ClassVar): Mapping of driver types to their
            corresponding classes.
    """

    _vm_driver_classes: ClassVar = {
        'qemu-driver': LibvirtDriver,
    }

    def get_vm_driver(self, db_virtual_machine: Dict) -> BaseVMDriver:
        """Create a VM driver instance based on the configuration.

        Args:
            db_virtual_machine (Dict): Dictionary containing the virtual
                machine configuration.

        Returns:
            BaseVMDriver: An instance of a virtual machine driver.

        Raises:
            KeyError: If the corresponding virtual machine type is not found.
        """
        vm_driver_class = self._vm_driver_classes[VM_DRIVER]
        return vm_driver_class(**db_virtual_machine)
