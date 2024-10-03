"""Module for serializing and deserializing storage data.

This module provides abstract and concrete classes for serializing and
deserializing storage data between different formats, including domain
objects, database objects, and web representations.

Classes:
    AbstractDataSerializer: Abstract base class defining the serialization
        interface.
    DataSerializer: Concrete implementation of the serialization interface
        for storage data.
"""

import abc
from typing import Dict, Type

from sqlalchemy import inspect

from openvair.modules.storage.adapters.orm import Storage


class AbstractDataSerializer(metaclass=abc.ABCMeta):
    """Abstract base class defining the serialization interface.

    This class provides the interface for serializing and deserializing
    storage data between different formats, including domain objects,
    database objects, and web representations.
    """

    @classmethod
    @abc.abstractmethod
    def to_domain(cls, storage: Storage) -> Dict:
        """Convert a database storage object to a domain dictionary.

        Args:
            storage (Storage): The storage object to convert.

        Returns:
            Dict: The converted domain dictionary.
        """
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def to_db(cls, data: Dict, orm_class: Type = Storage) -> Storage:
        """Convert a domain dictionary to a database storage object.

        Args:
            data (Dict): The domain dictionary to convert.
            orm_class (Type): The ORM class to use for the conversion.

        Returns:
            Storage: The converted database storage object.
        """
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def to_web(cls, storage: Storage) -> Dict:
        """Convert a database storage object to a web dictionary.

        Args:
            storage (Storage): The storage object to convert.

        Returns:
            Dict: The converted web dictionary.
        """
        raise NotImplementedError


class DataSerializer(AbstractDataSerializer):
    """Concrete implementation of the serialization interface for storage data.

    This class provides methods for serializing and deserializing storage data
    between domain objects, database objects, and web representations.
    """

    @classmethod
    def to_domain(cls, storage: Storage) -> Dict:
        """Convert a database storage object to a domain dictionary.

        This method takes a storage object and a list of extra specs, and
        returns a dictionary of the storage object with the extra specs added
        to it.

        Args:
            storage (Storage): The storage object to convert.

        Returns:
            Dict: The converted domain dictionary.
        """
        storage_dict = storage.__dict__.copy()
        storage_dict.update(
            {
                'id': str(storage_dict.get('id', '')),
                'user_id': str(storage_dict.get('user_id', '')),
            }
        )
        storage_dict.pop('_sa_instance_state')
        domain_extra_specs = []
        for spec in storage_dict.pop('extra_specs', []):
            edited_spec = spec.__dict__.copy()
            edited_spec.pop('_sa_instance_state')
            domain_extra_specs.append(edited_spec)
        storage_dict.update(
            **{spec['key']: spec['value'] for spec in domain_extra_specs}
        )
        return storage_dict

    @classmethod
    def to_db(cls, data: Dict, orm_class: Type = Storage) -> Storage:
        """Convert a domain dictionary to a database storage object.

        This method takes a dictionary and returns an object of the class
        Storage.

        Args:
            data (Dict): The domain dictionary to convert.
            orm_class (Type): The ORM class to use for the conversion.

        Returns:
            Storage: The converted database storage object.
        """
        orm_dict = {}
        inspected_orm_class = inspect(orm_class)
        for column in list(inspected_orm_class.columns):
            column_name = column.__dict__['key']
            orm_dict[column_name] = data.get(column_name)
        return orm_class(**orm_dict)

    @classmethod
    def to_web(cls, storage: Storage) -> Dict:
        """Convert a database storage object to a web dictionary.

        This method takes a storage object and a list of extra specs, and
        returns a dictionary of the storage object with the extra specs added
        to it.

        Args:
            storage (Storage): The storage object to convert.

        Returns:
            Dict: The converted web dictionary.
        """
        storage_dict = storage.__dict__.copy()
        storage_dict.update(
            {
                'id': str(storage_dict.get('id', '')),
                'user_id': str(storage_dict.get('user_id', '')),
            }
        )
        storage_dict.pop('_sa_instance_state')
        web_extra_specs = []
        for spec in storage_dict.pop('extra_specs', []):
            edited_spec = spec.__dict__.copy()
            edited_spec.pop('_sa_instance_state')
            web_extra_specs.append(edited_spec)
        storage_dict.update(
            {
                'storage_extra_specs': {
                    spec['key']: spec['value'] for spec in web_extra_specs
                }
            }
        )
        return storage_dict
