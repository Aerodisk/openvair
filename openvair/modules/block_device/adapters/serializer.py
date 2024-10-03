"""This module provides classes for serializing and deserializing ISCSIInterface

It includes an abstract base class `AbstractDataSerializer` which defines the
interface for converting ISCSIInterface objects to different formats, and a
concrete implementation `DataSerializer` which provides methods to convert
ISCSIInterface objects to domain, database, and web-friendly dictionaries.

Classes:
    AbstractDataSerializer: Abstract base class for data serialization.
    DataSerializer: Concrete implementation of AbstractDataSerializer.
"""

import abc
from typing import Dict

from sqlalchemy import inspect

from openvair.modules.block_device.adapters.orm import ISCSIInterface


class AbstractDataSerializer(metaclass=abc.ABCMeta):
    """Abstract class for data serialization.

    This class provides an interface for converting ISCSIInterface objects
    to different formats.
    """

    @classmethod
    @abc.abstractmethod
    def to_domain(cls, interface: ISCSIInterface) -> Dict:
        """Convert an ISCSIInterface object to a domain dictionary.

        Args:
            interface (ISCSIInterface): ORM object of the ISCSI interface.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.

        Returns:
            Dict: A dictionary representing the domain-specific attributes of
                the ISCSI interface.
        """
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def to_db(
        cls,
        data: dict,
        orm_class: ISCSIInterface = ISCSIInterface,
    ) -> ISCSIInterface:
        """Convert a dictionary to an ISCSIInterface ORM object.

        Args:
            data (dict): The dictionary with information about the interface.
            orm_class (ISCSIInterface, optional): The ORM class representing the
                ISCSI interface table. Defaults to ISCSIInterface.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.

        Returns:
            ISCSIInterface: ORM object of the ISCSI interface.
        """
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def to_web(cls, interface: ISCSIInterface) -> Dict:
        """Convert an ISCSIInterface object to a web dictionary.

        Args:
            interface (ISCSIInterface): The ORM object of the ISCSI interface.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.

        Returns:
            Dict: A dictionary representing the web attributes of the ISCSI
                interface.
        """
        raise NotImplementedError


class DataSerializer(AbstractDataSerializer):
    """Concrete implementation of AbstractDataSerializer.

    This class provides methods to serialize ISCSIInterface objects
    to different formats such as domain, database, and web.
    """

    @classmethod
    def to_domain(cls, interface: ISCSIInterface) -> Dict:
        """Convert an ISCSIInterface object to a domain dictionary.

        Args:
            interface (ISCSIInterface): ORM object of the ISCSI interface.

        Returns:
            Dict: A plain dictionary with the interface's information.
        """
        interface_dict = interface.__dict__.copy()
        interface_dict.pop('_sa_instance_state')
        interface_dict['id'] = str(interface_dict['id'])
        return interface_dict

    @classmethod
    def to_db(
        cls,
        data: Dict,
        orm_class: ISCSIInterface = ISCSIInterface,
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
        inspected_orm_class = inspect(orm_class)
        for column in list(inspected_orm_class.columns):
            column_name = column.__dict__['key']
            orm_dict[column_name] = data.get(column_name)
        return orm_class(**orm_dict)

    @classmethod
    def to_web(cls, interface: ISCSIInterface) -> Dict:
        """Convert an ISCSIInterface object to a web dictionary.

        Args:
            interface (ISCSIInterface): The interface object that you want to
                convert to a web-friendly format.

        Returns:
            Dict: A dictionary representing the web attributes of the ISCSI
                interface.
        """
        interface_dict = interface.__dict__.copy()
        interface_dict.pop('_sa_instance_state')
        interface_dict['id'] = str(interface_dict['id'])
        return interface_dict
