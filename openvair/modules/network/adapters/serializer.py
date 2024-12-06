"""This module provides classes for serializing and deserializing Interfaces

It includes a concrete implementation `DataSerializer` which provides methods
to convert Interface objects to domain, database, and web-friendly
dictionaries.

Classes:
    DataSerializer: Concrete implementation of AbstractDataSerializer.
"""

from typing import Dict, Type

from sqlalchemy import inspect

from openvair.abstracts.serializer import AbstractDataSerializer
from openvair.modules.network.adapters.orm import Interface


class DataSerializer(AbstractDataSerializer):
    """Implementation of AbstractDataSerializer for network interface data.

    This class provides methods for converting network interface data between
    domain models, ORM objects, and web representations.
    """

    @classmethod
    def to_domain(
        cls,
        orm_object: Interface,
    ) -> Dict:
        """Convert an Interface ORM object to a domain model dictionary.

        This method takes an Interface ORM object, converts it to a dictionary,
        removes ORM-specific metadata, and processes extra specifications.

        Args:
            orm_object (Interface): The Interface ORM object to convert.

        Returns:
            Dict: A dictionary representing the domain model.
        """
        interface_dict = orm_object.__dict__.copy()
        interface_dict['id'] = str(interface_dict['id'])
        interface_dict.pop('_sa_instance_state')
        domain_extra_specs = []
        for spec in interface_dict.pop('extra_specs'):
            converted_spec = spec.__dict__.copy()
            converted_spec['id'] = str(converted_spec['id'])
            converted_spec.pop('_sa_instance_state')
            domain_extra_specs.append(converted_spec)
        interface_dict.update(
            **{spec['key']: spec['value'] for spec in domain_extra_specs}
        )
        return interface_dict

    @classmethod
    def to_db(
        cls,
        data: Dict,
        orm_class: Type = Interface,
    ) -> Interface:
        """Convert a dictionary to an ORM object.

        This method takes a dictionary of data and returns an instance of the
        specified ORM class populated with the dictionary values.

        Args:
            data (Dict): A dictionary containing the data to be converted.
            orm_class (Type): The ORM class to instantiate with the provided
                data. Defaults to Interface.

        Returns:
            Interface: An ORM object created from the dictionary data.
        """
        orm_dict = {}
        inspected_orm_class = inspect(orm_class)
        for column in list(inspected_orm_class.columns):
            column_name = column.__dict__['key']
            orm_dict[column_name] = data.get(column_name)
        return orm_class(**orm_dict)

    @classmethod
    def to_web(
        cls,
        orm_object: Interface,
    ) -> Dict:
        """Convert an Interface ORM object to a dictionary for web output.

        This method takes an Interface ORM object, processes its extra
        specifications, and returns a dictionary formatted for web output.

        Args:
            orm_object (Interface): The Interface ORM object to convert.

        Returns:
            Dict: A dictionary formatted for web output.
        """
        interface_dict = orm_object.__dict__.copy()
        interface_dict['id'] = str(interface_dict['id'])
        interface_dict.pop('_sa_instance_state')
        web_extra_specs = []
        for spec in interface_dict.pop('extra_specs', []):
            converted_spec = spec.__dict__.copy()
            converted_spec.pop('_sa_instance_state')
            web_extra_specs.append(converted_spec)
        interface_dict.update(
            {
                'interface_extra_specs': {
                    spec['key']: spec['value'] for spec in web_extra_specs
                }
            }
        )
        return interface_dict
