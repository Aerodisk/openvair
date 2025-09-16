"""This module provides classes for serializing and deserializing VirtualMachine

It includes a concrete implementation `DataSerializer` which provides methods
to convert VirtualMachine objects to domain, database, and web-friendly
dictionaries.

Classes:
    DataSerializer: Concrete implementation of AbstractDataSerializer.
"""

from typing import TYPE_CHECKING, Dict, Type, Union, cast

from sqlalchemy import inspect

from openvair.abstracts.serializer import AbstractDataSerializer
from openvair.modules.virtual_machines.adapters import orm
from openvair.libs.data_handlers.json.serializer import deserialize_json

if TYPE_CHECKING:
    from sqlalchemy.orm.mapper import Mapper


class DataSerializer(AbstractDataSerializer):
    """Concrete implementation of AbstractDataSerializer.

    This class provides methods to serialize and deserialize virtual machine
    data between domain models, database models, and web representations.
    """

    @classmethod
    def to_domain(
        cls,
        orm_object: orm.VirtualMachines,
    ) -> Dict:
        """Convert a VirtualMachine ORM model to a domain model.

        Args:
            cls: The class that we're converting to.
            orm_object (VirtualMachine): VirtualMachine

        Returns:
            A dictionary of the virtual machine's data.
        """
        data = orm_object.__dict__.copy()
        data.pop('_sa_instance_state')
        data.update({'id': str(data.get('id', ''))})
        return data

    @classmethod
    def to_db(
        cls,
        data: Dict,
        orm_class: Union[
            Type[orm.VirtualMachines],
            Type[orm.CpuInfo],
            Type[orm.Os],
            Type[orm.Disk],
            Type[orm.VirtualInterface],
            Type[orm.ProtocolGraphicInterface],
            Type[orm.RAM],
        ] = orm.VirtualMachines,
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
        inspected_orm_class = cast('Mapper', inspect(orm_class))
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
                    'qos': deserialize_json(data.get('qos', ''))
                    if isinstance(data.get('qos', ''), str)
                    else data.get('qos', '')
                }
            )
        return data

    @classmethod
    def vm_to_web(
        cls,
        virtual_machine: orm.VirtualMachines,
    ) -> Dict:
        """Convert a VirtualMachine ORM model to a detailed web representation.

        This method includes related entities such as CPU, OS, disks, etc.

        Args:
            virtual_machine (orm.VirtualMachines): The virtual machine ORM model
                instance.

        Returns:
            Dict: A dictionary representing the detailed web model with related
                entities.
        """
        vm_dict: Dict = virtual_machine.__dict__.copy()
        vm_dict.pop('_sa_instance_state')
        vm_dict.update(
            {
                'id': str(vm_dict['id']),
                'cpu': cls.to_web(vm_dict.get('cpu', {})),
                'os': cls.to_web(vm_dict.get('os', {})),
                'graphic_interface': cls.to_web(
                    vm_dict.get('graphic_interface', {})
                ),
                'virtual_interfaces': [
                    cls.to_web(interface)
                    for interface in vm_dict.get('virtual_interfaces', [])
                ],
                'ram': cls.to_web(vm_dict.get('ram', {})),
                'disks': [
                    cls.to_web(disk) for disk in vm_dict.get('disks', [])
                ],
                'user_id': str(vm_dict.get('user_id', '')),
            }
        )
        return vm_dict

    @classmethod
    def snapshot_to_db(
        cls,
        data: Dict,
        orm_class: Type[orm.Snapshots] = orm.Snapshots,
    ) -> orm.Snapshots:
        """Convert a dictionary to a Snapshots ORM model.

        Args:
            data (Dict): A dictionary containing snapshot data to populate the
            ORM model.
            orm_class (Type[orm.Snapshots]): The ORM class to instantiate
            (default: orm.Snapshots).

        Returns:
            orm.Snapshots: An instance of Snapshots ORM class populated with
            the provided data.
        """
        orm_dict = {}
        inspected_orm_class = cast('Mapper', inspect(orm_class))
        for column in list(inspected_orm_class.columns):
            column_name = column.__dict__['key']
            if data.get(column_name) is None:
                continue
            orm_dict[column_name] = data.get(column_name)
        return orm_class(**orm_dict)

    @classmethod
    def snapshot_to_web(
        cls,
        snapshot: orm.Snapshots,
    ) -> Dict:
        """Convert a Snapshots ORM model to a detailed web representation.

        Args:
            snapshot (orm.Snapshots): The snapshot ORM model instance
            to convert.

        Returns:
            Dict: A dictionary representing the web model of snapshot
        """
        if not snapshot:
            return {}
        data = snapshot.__dict__.copy()
        data.pop('_sa_instance_state', None)
        data.pop('created_at', None)
        data['id'] = str(data.get('id', ''))
        data['vm_id'] = str(data.get('vm_id', ''))
        data['created_at'] = snapshot.created_at.isoformat()
        parent_data = None
        if hasattr(snapshot, 'parent') and snapshot.parent:
            parent_data = {
                'id': str(snapshot.parent.id),
                'name': snapshot.parent.name,
                'status': snapshot.parent.status,
            }
        data.pop('parent', None)
        data['parent'] = parent_data
        data.pop('parent_id', None)
        data.pop('virtual_machine', None)
        return data
