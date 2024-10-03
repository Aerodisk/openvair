"""Module for data serialization related to virtual machines.

This module provides an abstract base class and a concrete implementation
for serializing and deserializing virtual machine data between domain models,
database models, and web representations. The serialization handles various
ORM entities associated with virtual machines, ensuring that the data is
properly transformed for each use case.

Classes:
    AbstractDataSerializer: Abstract base class defining the interface for
        data serialization and deserialization.
    DataSerializer: Concrete implementation of the AbstractDataSerializer
        that handles serialization and deserialization of virtual machine
        data between different representations.
"""

import abc
import json
from typing import Dict, Type, Union

from sqlalchemy import inspect

from openvair.modules.virtual_machines.adapters import orm


class AbstractDataSerializer(metaclass=abc.ABCMeta):
    """Abstract base class for virtual machine data serialization.

    This class defines the methods required for converting virtual machine
    data between domain models, database models, and web representations.
    """

    @classmethod
    @abc.abstractmethod
    def to_domain(cls, virtual_machine: orm.VirtualMachines) -> Dict:
        """Convert a database model to a domain model.

        Args:
            virtual_machine (orm.VirtualMachines): The ORM model instance to
                convert.

        Returns:
            Dict: A dictionary representing the domain model.
        """
        pass

    @classmethod
    @abc.abstractmethod
    def to_db(
        cls,
        data: Dict,
        orm_class: Type,
    ) -> Union[
        orm.VirtualMachines,
        orm.CpuInfo,
        orm.Os,
        orm.Disk,
        orm.VirtualInterface,
        orm.ProtocolGraphicInterface,
        orm.RAM,
    ]:
        """Convert a dictionary to a database model.

        Args:
            data (Dict): A dictionary containing the data to populate the ORM
                model.
            orm_class (Type): The ORM class to instantiate with the data.

        Returns:
            Union: An instance of the specified ORM class populated with
                theprovided data.
        """
        pass

    @classmethod
    @abc.abstractmethod
    def to_web(
        cls,
        orm_object: Union[
            orm.VirtualMachines,
            orm.CpuInfo,
            orm.Os,
            orm.Disk,
            orm.VirtualInterface,
            orm.ProtocolGraphicInterface,
            orm.RAM,
        ],
    ) -> Dict:
        """Convert a database model to a web representation.

        Args:
            orm_object (Union): The ORM model instance to convert.

        Returns:
            Dict: A dictionary representing the web model.
        """
        pass

    @classmethod
    @abc.abstractmethod
    def vm_to_web(cls, virtual_machine: orm.VirtualMachines) -> Dict:
        """Convert a virtual machine model to a detailed web representation.

        Args:
            virtual_machine (orm.VirtualMachines): The virtual machine ORM model
                instance.

        Returns:
            Dict: A dictionary representing the detailed web model.
        """
        pass


class DataSerializer(AbstractDataSerializer):
    """Concrete implementation of AbstractDataSerializer.

    This class provides methods to serialize and deserialize virtual machine
    data between domain models, database models, and web representations.
    """

    @classmethod
    def to_domain(cls, virtual_machine: orm.VirtualMachines) -> Dict:
        """Convert a VirtualMachine ORM model to a domain model.

        Args:
            virtual_machine (orm.VirtualMachines): The ORM model instance to
                convert.

        Returns:
            Dict: A dictionary representing the domain model, with the 'id'
                field converted to a string.
        """
        data = virtual_machine.__dict__.copy()
        data.pop('_sa_instance_state')
        data.update({'id': str(data.get('id', ''))})
        return data

    @classmethod
    def to_db(
        cls,
        data: Dict,
        orm_class: Type,
    ) -> Union[
        orm.VirtualMachines,
        orm.CpuInfo,
        orm.Os,
        orm.Disk,
        orm.VirtualInterface,
        orm.ProtocolGraphicInterface,
        orm.RAM,
    ]:
        """Convert a dictionary to an ORM model.

        Args:
            data (Dict): A dictionary containing the data to populate the ORM
                model.
            orm_class (Type): The ORM class to instantiate with the data.

        Returns:
            Union:
            An instance of the specified ORM class populated with the provided
                data.
        """
        orm_dict = {}
        inspected_orm_class = inspect(orm_class)
        for column in list(inspected_orm_class.columns):
            column_name = column.__dict__['key']
            if not data.get(column_name):
                continue
            orm_dict[column_name] = data.get(column_name)
        return orm_class(**orm_dict)

    @classmethod
    def to_web(  # noqa: C901 because all checking is needed here may be will need be to refact
        cls,
        orm_object: Union[
            orm.VirtualMachines,
            orm.CpuInfo,
            orm.Os,
            orm.Disk,
            orm.VirtualInterface,
            orm.ProtocolGraphicInterface,
            orm.RAM,
        ],
    ) -> Dict:
        """Convert an ORM model to a web representation.

        Args:
            orm_object (Union): The ORM model instance to convert.

        Returns:
            Dict: A dictionary representing the web model, with certain fields
            converted to appropriate formats (e.g., 'id' and 'vm_id' as
                strings).
        """
        if not orm_object:
            return {}
        data = orm_object.__dict__.copy()
        data.pop('_sa_instance_state')
        data['id'] = str(data.get('id', ''))
        if data.get('virtual_machine', None):
            data.pop('virtual_machine')
        if data.get('vm_id', None):
            data.update({'vm_id': str(data.get('vm_id'))})
        if data.get('volume_id', None):
            data.update({'volume_id': str(data.get('volume_id'))})
        if data.get('disk_id', None):
            data.update({'disk_id': str(data.get('disk_id'))})
        if data.get('qos', ''):
            data.update(
                {
                    'qos': json.loads(data.get('qos', ''))
                    if isinstance(data.get('qos', ''), str)
                    else data.get('qos', '')
                }
            )
        return data

    @classmethod
    def vm_to_web(cls, virtual_machine: orm.VirtualMachines) -> Dict:
        """Convert a VirtualMachine ORM model to a detailed web representation.

        This method includes related entities such as CPU, OS, disks, etc.

        Args:
            virtual_machine (orm.VirtualMachines): The virtual machine ORM model
                instance.

        Returns:
            Dict: A dictionary representing the detailed web model with related
                entities.
        """
        vm_dict = virtual_machine.__dict__.copy()
        vm_dict.pop('_sa_instance_state')
        vm_dict.update(
            {
                'id': str(vm_dict['id']),
                'cpu': cls.to_web(vm_dict.get('cpu')),
                'os': cls.to_web(vm_dict.get('os')),
                'graphic_interface': cls.to_web(
                    vm_dict.get('graphic_interface')
                ),
                'virtual_interfaces': [
                    cls.to_web(interface)
                    for interface in vm_dict.get('virtual_interfaces')
                ],
                'ram': cls.to_web(vm_dict.get('ram')),
                'disks': [cls.to_web(disk) for disk in vm_dict.get('disks')]
                if vm_dict.get('disks')
                else [],
                'user_id': str(vm_dict.get('user_id', '')),
            }
        )
        return vm_dict
