"""This module provides classes for serializing and deserializing Users

It includes a concrete implementation `DataSerializer` which provides methods
to convert User objects to domain, database, and web-friendly
dictionaries.

Classes:
    DataSerializer: Concrete implementation of AbstractDataSerializer.
"""

from typing import Dict, Type

from sqlalchemy import inspect

from openvair.abstracts.serializer import AbstractDataSerializer
from openvair.modules.user.adapters.orm import User


class DataSerializer(AbstractDataSerializer):
    """Concrete implementation of AbstractDataSerializer using SQLAlchemy.

    This class provides the actual implementation for converting user data
    between domain models, database models, and web representations.

    Methods:
        to_domain: Converts a user database model to a domain model dictionary.
        to_db: Converts a domain model dictionary to a user database model.
        to_web: Converts a user database model to a web representation
            dictionary.
    """

    @classmethod
    def to_domain(
        cls,
        orm_object: User,
    ) -> Dict:
        """Convert a user database model to a domain model dictionary.

        Args:
            orm_object (User): The user database model.

        Returns:
            Dict: The user data as a domain model dictionary.
        """
        data = orm_object.__dict__.copy()
        data.pop('_sa_instance_state')
        data.update({'id': str(data.get('id', ''))})
        return data

    @classmethod
    def to_db(
        cls,
        data: Dict,
        orm_class: Type = User,
    ) -> User:
        """Convert a domain model dictionary to a user database model.

        Args:
            data (dict): The user data as a domain model dictionary.
            orm_class: db table

        Returns:
            User: The user database model.
        """
        orm_dict = {}
        inspected_orm_class = inspect(orm_class)
        for column in list(inspected_orm_class.columns):
            column_name = column.__dict__['key']
            orm_dict[column_name] = data.get(column_name)

        return User(**orm_dict)

    @classmethod
    def to_web(
        cls,
        orm_object: User,
    ) -> Dict:
        """Convert a user database model to a web representation dictionary.

        Args:
            orm_object (User): The user database model.

        Returns:
            Dict: The user data as a web representation dictionary.
        """
        data = orm_object.__dict__.copy()
        data.pop('_sa_instance_state')  # Remove SQLAlchemy state information
        data.update({'id': str(data.get('id', ''))})
        return data
