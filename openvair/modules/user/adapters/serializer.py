"""Serializer layer for user data.

This module defines the abstract and concrete serializers for converting
user data between domain models, database models, and web representations.

Classes:
    AbstractDataSerializer: Abstract base class for user data serialization.
    DataSerializer: Concrete implementation of AbstractDataSerializer
        using SQLAlchemy ORM for user data.

Methods:
    AbstractDataSerializer.to_domain: Abstract method to convert a user
        database model to a domain model dictionary.
    AbstractDataSerializer.to_db: Abstract method to convert a domain model
        dictionary to a user database model.
    AbstractDataSerializer.to_web: Abstract method to convert a user
        database model to a web representation dictionary.
    DataSerializer.to_domain: Converts a user database model to a domain
        model dictionary.
    DataSerializer.to_db: Converts a domain model dictionary to a user
        database model.
    DataSerializer.to_web: Converts a user database model to a web
        representation dictionary.
"""

import abc
from typing import Dict

from sqlalchemy import inspect

from openvair.modules.user.adapters.orm import User


class AbstractDataSerializer(metaclass=abc.ABCMeta):
    """Abstract base class for user data serialization.

    This class defines the interface for converting user data between
    domain models, database models, and web representations.

    Methods:
        to_domain: Convert a user database model to a domain model dictionary.
        to_db: Convert a domain model dictionary to a user database model.
        to_web: Convert a user database model to a web representation
            dictionary.
    """

    @classmethod
    @abc.abstractmethod
    def to_domain(cls, user: User) -> Dict:
        """Convert a user database model to a domain model dictionary.

        Args:
            user (User): The user database model.

        Returns:
            Dict: The user data as a domain model dictionary.
        """
        ...

    @classmethod
    @abc.abstractmethod
    def to_db(cls, data: Dict) -> User:
        """Convert a domain model dictionary to a user database model.

        Args:
            data (Dict): The user data as a domain model dictionary.

        Returns:
            User: The user database model.
        """
        ...

    @classmethod
    @abc.abstractmethod
    def to_web(cls, user: User) -> Dict:
        """Convert a user database model to a web representation dictionary.

        Args:
            user (User): The user database model.

        Returns:
            Dict: The user data as a web representation dictionary.
        """
        ...


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
    def to_domain(cls, user: User) -> Dict:
        """Convert a user database model to a domain model dictionary.

        Args:
            user (User): The user database model.

        Returns:
            Dict: The user data as a domain model dictionary.
        """
        data = user.__dict__.copy()
        data.pop('_sa_instance_state')
        data.update({'id': str(data.get('id', ''))})
        return data

    @classmethod
    def to_db(cls, domain: Dict) -> User:
        """Convert a domain model dictionary to a user database model.

        Args:
            domain (Dict): The user data as a domain model dictionary.

        Returns:
            User: The user database model.
        """
        orm_dict = {}
        inspected_orm_class = inspect(User)
        for column in list(inspected_orm_class.columns):
            column_name = column.__dict__['key']
            orm_dict[column_name] = domain.get(column_name)

        return User(**orm_dict)

    @classmethod
    def to_web(cls, user: User) -> Dict:
        """Convert a user database model to a web representation dictionary.

        Args:
            user (User): The user database model.

        Returns:
            Dict: The user data as a web representation dictionary.
        """
        data = user.__dict__.copy()
        data.pop('_sa_instance_state')  # Remove SQLAlchemy state information
        data.update({'id': str(data.get('id', ''))})
        return data
