"""This module provides classes for serializing and deserializing Events.

It includes a concrete implementation `DataSerializer` which provides methods
to convert Events objects to domain, database, and web-friendly dictionaries.

Classes:
    DataSerializer: Concrete implementation of AbstractDataSerializer.
"""

from typing import Dict, Type, cast

from sqlalchemy import inspect
from sqlalchemy.orm.mapper import Mapper

from openvair.abstracts.serializer import AbstractDataSerializer
from openvair.modules.event_store.adapters.orm import Events


class DataSerializer(AbstractDataSerializer):
    """Concrete implementation of AbstractDataSerializer.

    This class provides methods for serializing data to and from Events ORM
    objects.
    """

    @classmethod
    def to_db(
        cls,
        data: Dict,
        orm_class: Type[Events] = Events,
    ) -> Events:
        """Convert web data to a database ORM object.

        This method inspects the ORM class columns and populates the ORM object
        with data from the provided dictionary.

        Args:
            data (Dict): Data to be converted to an ORM object.
            orm_class (Events): The ORM class to instantiate.

        Returns:
            Events: The ORM object created from the data.
        """
        orm_dict = {}
        inspected_orm_class = cast(Mapper, inspect(orm_class))
        for column in list(inspected_orm_class.columns):
            column_name = column.__dict__['key']
            value = data.get(column_name)
            if not value and not isinstance(value, int):
                continue
            orm_dict[column_name] = data.get(column_name)
        return orm_class(**orm_dict)

    @classmethod
    def to_web(
        cls,
        orm_object: Events,
    ) -> Dict:
        """Convert a database ORM object to web data.

        This method converts the ORM object to a dictionary and modifies certain
        fields for web compatibility.

        Args:
            orm_object (Events): The ORM object to be converted to web data.

        Returns:
            Dict: The web data created from the ORM object.
        """
        event_dict = orm_object.__dict__.copy()
        event_dict.pop('_sa_instance_state')
        event_dict.update(
            {
                'object_id': str(event_dict.get('object_id', '')),
                'user_id': str(event_dict.get('user_id', '')),
                'timestamp': int(round(event_dict['timestamp'].timestamp())),
            }
        )
        return event_dict
