"""Serialization and deserialization for notifications.

This module provides functionality to serialize and deserialize Notification
objects between domain, database, and web formats.
"""

import abc
from typing import Dict

from sqlalchemy import inspect

from openvair.modules.notification.adapters.orm import Notification


class AbstractDataSerializer(metaclass=abc.ABCMeta):
    """Abstract base class for notification serializers."""

    @classmethod
    @abc.abstractmethod
    def to_domain(cls, notification: Notification) -> Dict:
        """Convert a Notification object to a domain dictionary.

        Args:
            notification (Notification): The notification object to convert.

        Returns:
            Dict: A dictionary representation of the domain object.
        """
        ...

    @classmethod
    @abc.abstractmethod
    def to_db(cls, data: Dict, orm_class: type = Notification) -> Notification:
        """Convert a dictionary to an ORM Notification object.

        Args:
            data (Dict): The dictionary to convert.
            orm_class (type): The ORM class to instantiate.

        Returns:
            Notification: The ORM Notification object.
        """
        ...

    @classmethod
    @abc.abstractmethod
    def to_web(cls, notification: Notification) -> Dict:
        """Convert a Notification object to a dictionary for web output.

        Args:
            notification (Notification): The notification object to convert.

        Returns:
            Dict: A dictionary representation for web output.
        """
        ...


class DataSerializer(AbstractDataSerializer):
    """Serializer for converting Notification objects between formats."""

    @classmethod
    def to_domain(cls, notification: Notification) -> Dict:
        """Convert a Notification object to a domain dictionary.

        It takes a Notification object and returns a dictionary with the same
        data, but with the id converted to a string. In addition, it removes
        metadata of ORM.

        Args:
            notification (Notification): Notification object of ORM to be
                converted to a dictionary.

        Returns:
            Dict: A dictionary representation of the domain object.
        """
        notification_dict = notification.__dict__.copy()
        notification_dict.pop('_sa_instance_state')
        notification_dict.update(
            {
                'id': str(notification_dict.get('id', '')),
                'create_datetime': str(
                    notification_dict.get('create_datetime', '')
                ),
            }
        )

        return notification_dict

    @classmethod
    def to_db(cls, data: Dict, orm_class: type = Notification) -> Notification:
        """Convert a dictionary to an ORM Notification object.

        Takes a dictionary of data and returns an instance of the specified ORM
        class with the data from this dictionary.

        Args:
            data (Dict): A dictionary containing the data to be converted.
            orm_class (type): The ORM class to convert the dictionary to. If not
                specified, defaults to Notification.

        Returns:
            Notification: An instance of orm_class with the values from the
                data dictionary.
        """
        orm_dict = {}
        inspected_orm_class = inspect(orm_class)
        for column in list(inspected_orm_class.columns):
            column_name = column.__dict__['key']
            orm_dict[column_name] = data.get(column_name)
        return orm_class(**orm_dict)

    @classmethod
    def to_web(cls, notification: Notification) -> Dict:
        """Convert a Notification object to a dictionary for web output.

        It takes a Notification object and returns a dictionary with the
        same data, but with the id field converted to a string.

        Args:
            notification (Notification): The notification object to convert.

        Returns:
            Dict: A dictionary representation for web output.
        """
        notification_dict = notification.__dict__.copy()
        notification_dict.pop('_sa_instance_state')
        notification_dict.update(
            {
                'id': str(notification_dict['id']),
            }
        )

        return notification_dict
