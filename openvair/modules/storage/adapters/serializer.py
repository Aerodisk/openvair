"""This module provides classes for serializing and deserializing Storages

It includes a concrete implementation `DataSerializer` which provides methods
to convert Storage objects to domain, database, and web-friendly
dictionaries.

Classes:
    DataSerializer: Concrete implementation of AbstractDataSerializer.
"""

from typing import Dict, Type, Union, cast

from sqlalchemy import inspect
from sqlalchemy.orm.mapper import Mapper

from openvair.abstracts.serializer import AbstractDataSerializer
from openvair.modules.storage.adapters.orm import Storage, StorageExtraSpecs


class DataSerializer(AbstractDataSerializer):
    """Concrete implementation of the serialization interface for storage data.

    This class provides methods for serializing and deserializing storage data
    between domain objects, database objects, and web representations.
    """

    @classmethod
    def to_domain(
        cls,
        orm_object: Storage,
    ) -> Dict:
        """Its get dictonary of data about the storage

        This method takes a storage object and a list of extra specs, and
        returns a dictionary of the storage object with the extra specs added
        to it.

        Args:
            cls: The class that is being converted to a domain object.
            orm_object (Storage): Storage

        Returns:
            Dict: The converted domain dictionary.
        """
        storage_dict = orm_object.__dict__.copy()
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
    def to_db(
        cls,
        data: Dict,
        orm_class: Union[Type[Storage], Type[StorageExtraSpecs]] = Storage,
    ) -> Union[Storage, StorageExtraSpecs]:
        """It takes a dictionary and returns an object of the class Storage

        Args:
            data (Dict): The domain dictionary to convert.
            orm_class (Type): The ORM class to use for the conversion.

        Returns:
            Storage: The converted database storage object.
        """
        orm_dict = {}
        inspected_orm_class = cast(Mapper, inspect(orm_class))
        for column in list(inspected_orm_class.columns):
            column_name = column.__dict__['key']
            orm_dict[column_name] = data.get(column_name)
        return orm_class(**orm_dict)

    @classmethod
    def to_web(
        cls,
        orm_object: Storage,
    ) -> Dict:
        """It takes a dictionary and returns an object of the class Storage

        This method takes a storage object and a list of extra specs, and
        returns a dictionary of the storage object with the extra specs added
        to it.

        Args:
            cls: The class of the object that is being converted.
            orm_object: The storage object that we're converting to a
                dictionary.

        Returns:
            Dict: The converted web dictionary.
        """
        storage_dict = orm_object.__dict__.copy()
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
