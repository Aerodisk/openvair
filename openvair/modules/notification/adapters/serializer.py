"""This module provides classes for serializing and deserializing Notifications

It includes a concrete implementation `DataSerializer` which provides methods
to convert Notification objects to domain, database, and web-friendly
dictionaries.

Classes:
    DataSerializer: Concrete implementation of AbstractDataSerializer.
"""

from typing import Dict, Type

from sqlalchemy import inspect

from openvair.abstracts.serializer import AbstractDataSerializer
from openvair.modules.notification.adapters.orm import Notification


class DataSerializer(AbstractDataSerializer):
    """Serializer for converting Notification objects between formats."""

    @classmethod
    def to_domain(
        cls,
        orm_object: Notification,
    ) -> Dict:
        """Function for converting SQLAlchemy object to dictionary.

        It takes a Notification object and returns a dictionary with the same
        data, but with the id converted to a string. In addition, it removes
        metadata of ORM.

        Args:
            orm_object (Notification): Notification object of ORM to be
            converted to a dictionary.

        Returns:
            Dict: A dictionary representation of the domain object.
        """
        notification_dict = orm_object.__dict__.copy()
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
    def to_db(
        cls,
        data: Dict,
        orm_class: Type = Notification,
    ) -> Notification:
        """Converts a dictionary to an SQLAlchemy object.

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
    def to_web(
        cls,
        orm_object: Notification,
    ) -> Dict:
        """Function for converting SQLAlchemy object to dictionary for web.

        It takes a Notification object and returns a dictionary with the
        same data, but with the id field converted to a string.

        Args:
          orm_object (Notification): The notification object to convert.

        Returns:
            Dict: A dictionary representation for web output.
        """
        notification_dict = orm_object.__dict__.copy()
        notification_dict.pop('_sa_instance_state')
        notification_dict.update(
            {
                'id': str(notification_dict['id']),
            }
        )

        return notification_dict
