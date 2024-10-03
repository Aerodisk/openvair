"""Module for serializing and deserializing image data.

This module defines abstract and concrete classes for converting image data
between different formats, including domain objects, database objects, and
web representations. It facilitates the conversion of image entities for
various use cases, such as storage in the database or presentation in a web
API.

Classes:
    AbstractDataSerializer: Abstract base class defining the interface for
        serializing and deserializing image data.
    DataSerializer: Concrete implementation of AbstractDataSerializer that
        provides methods to convert image data between different formats.
"""

import abc
from typing import Dict, Type

from sqlalchemy import inspect

from openvair.modules.image.adapters.orm import Image


class AbstractDataSerializer(metaclass=abc.ABCMeta):
    """Abstract base class for serializing and deserializing image data.

    This class defines the interface for converting image objects between
    different formats, such as domain models, database models, and web
    representations.
    """

    @classmethod
    @abc.abstractmethod
    def to_domain(cls, image: Image) -> Dict:
        """Convert an Image ORM object to a domain model dictionary.

        Args:
            image (Image): The Image ORM object to convert.

        Returns:
            Dict: A dictionary representing the domain model.
        """
        ...

    @classmethod
    @abc.abstractmethod
    def to_db(
        cls,
        data: Dict,
        orm_class: Type = Image,
    ) -> Image:
        """Convert a dictionary to an ORM object.

        Args:
            data (Dict): A dictionary containing the data to be converted.
            orm_class (Type): The ORM class to instantiate with the provided
                data. Defaults to Image.

        Returns:
            Image: An ORM object created from the dictionary data.
        """
        ...

    @classmethod
    @abc.abstractmethod
    def to_web(cls, image: Image) -> Dict:
        """Convert an Image ORM object to a dictionary for web representation.

        Args:
            image (Image): The Image ORM object to convert.

        Returns:
            Dict: A dictionary formatted for web output.
        """
        ...


class DataSerializer(AbstractDataSerializer):
    """Concrete implementation of AbstractDataSerializer for image data.

    This class provides methods for converting image data between domain models,
    ORM objects, and web representations.
    """

    @classmethod
    def to_domain(cls, image: Image) -> Dict:
        """Convert an Image ORM object to a domain model dictionary.

        This method takes an Image ORM object and returns a dictionary
        representing the domain model. The ID, storage ID, and user ID are
        converted to strings, and ORM-specific metadata is removed.

        Args:
            image (Image): The Image ORM object to convert.

        Returns:
            Dict: A dictionary representing the domain model.
        """
        image_dict = image.__dict__.copy()
        image_dict.pop('_sa_instance_state')
        image_dict.pop('attachments')
        image_dict.update(
            {
                'id': str(image_dict.get('id', '')),
                'storage_id': str(image_dict.get('storage_id', '')),
                'user_id': str(image_dict.get('user_id', '')),
            }
        )
        return image_dict

    @classmethod
    def to_db(cls, data: Dict, orm_class: Type = Image) -> Image:
        """Convert a dictionary to an ORM object.

        This method takes a dictionary of data and returns an instance of the
        specified ORM class populated with the dictionary values.

        Args:
            data (Dict): A dictionary containing the data to be converted.
            orm_class (Type): The ORM class to instantiate with the provided
                data. Defaults to Image.

        Returns:
            Image: An ORM object created from the dictionary data.
        """
        orm_dict = {}
        inspected_orm_class = inspect(orm_class)
        for column in list(inspected_orm_class.columns):
            column_name = column.__dict__['key']
            value = data.get(column_name)
            if not value and not isinstance(value, int):
                continue
            orm_dict[column_name] = data.get(column_name)
        return orm_class(**orm_dict)

    @classmethod
    def to_web(cls, image: Image) -> Dict:
        """Convert an Image ORM object to a dictionary for web representation.

        This method takes an Image ORM object and returns a dictionary formatted
        for web output. The ID and storage ID are converted to strings, and
        the size field is converted to an integer. Attachments are also
        processed and included in the output.

        Args:
            image (Image): The Image ORM object to convert.

        Returns:
            Dict: A dictionary formatted for web output.
        """
        image_dict = image.__dict__.copy()
        image_dict.pop('_sa_instance_state')
        attachments = []
        for attachment in image_dict.pop('attachments', []):
            converted_attachment = attachment.__dict__.copy()
            converted_attachment.pop('_sa_instance_state')
            converted_attachment.update(
                {
                    'image_id': str(converted_attachment.get('image_id', '')),
                    'vm_id': str(converted_attachment.get('vm_id', '')),
                    'user_id': str(converted_attachment.get('user_id', '')),
                }
            )
            attachments.append(converted_attachment)
        image_dict.update(
            {
                'id': str(image_dict['id']),
                'storage_id': str(image_dict['storage_id']),
                'user_id': str(image_dict.get('user_id', '')),
                'attachments': attachments,
            }
        )
        return image_dict
