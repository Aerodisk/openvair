"""This module provides classes for serializing and deserializing ISCSIInterface

It includes a concrete implementation `DataSerializer` which provides methods
to convert ISCSIInterface objects to domain, database, and web-friendly
dictionaries.

Classes:
    DataSerializer: Concrete implementation of AbstractDataSerializer.
"""

from typing import TYPE_CHECKING, cast

from sqlalchemy import inspect

from openvair.abstracts.serializer import AbstractDataSerializer
from openvair.modules.block_device.adapters.orm import ISCSIInterface

if TYPE_CHECKING:
    from sqlalchemy.orm.mapper import Mapper


class DataSerializer(AbstractDataSerializer):
    """Concrete implementation of AbstractDataSerializer.

    This class provides methods to serialize ISCSIInterface objects
    to different formats such as domain, database, and web.
    """

    @classmethod
    def to_domain(
        cls,
        orm_object: ISCSIInterface,
    ) -> dict:
        """Convert an ISCSIInterface object to a domain dictionary.

        Args:
            orm_object (ISCSIInterface): ORM object of the ISCSI interface.

        Returns:
            Dict: A plain dictionary with the interface's information.
        """
        interface_dict = orm_object.__dict__.copy()
        interface_dict.pop('_sa_instance_state')
        interface_dict['id'] = str(interface_dict['id'])
        return interface_dict

    @classmethod
    def to_db(
        cls,
        data: dict,
        orm_class: type[ISCSIInterface] = ISCSIInterface,
    ) -> ISCSIInterface:
        """Convert a dictionary to an ISCSIInterface ORM object.

        Args:
            data (Dict): The dictionary with information about the interface.
            orm_class (ISCSIInterface, optional): The ORM class representing the
                ISCSI interface table. Defaults to ISCSIInterface.

        Returns:
            ISCSIInterface: ORM object of the ISCSI interface.
        """
        orm_dict = {}
        inspected_orm_class = cast('Mapper', inspect(orm_class))
        for column in list(inspected_orm_class.columns):
            column_name = column.__dict__['key']
            orm_dict[column_name] = data.get(column_name)
        return orm_class(**orm_dict)

    @classmethod
    def to_web(
        cls,
        orm_object: ISCSIInterface,
    ) -> dict:
        """Convert an ISCSIInterface object to a web dictionary.

        Args:
            orm_object (ISCSIInterface): The interface object that you want to
                convert to a web-friendly format.

        Returns:
            Dict: A dictionary representing the web attributes of the ISCSI
                interface.
        """
        interface_dict = orm_object.__dict__.copy()
        interface_dict.pop('_sa_instance_state')
        interface_dict['id'] = str(interface_dict['id'])
        return interface_dict
