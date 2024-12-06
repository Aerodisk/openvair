"""This module provides classes for serializing and deserializing Volumes

It includes a concrete implementation `DataSerializer` which provides methods
to convert Volume objects to domain, database, and web-friendly
dictionaries.

Classes:
    DataSerializer: Concrete implementation of AbstractDataSerializer.
"""

from typing import Dict, Type

from sqlalchemy import inspect

from openvair.abstracts.serializer import AbstractDataSerializer
from openvair.modules.volume.adapters.orm import Volume


class DataSerializer(AbstractDataSerializer):
    """Concrete implementation of the data serializer.

    This class provides methods to convert volume data between domain models,
    database objects, and web responses.
    """

    @classmethod
    def to_domain(cls, volume: Volume) -> Dict:
        """Convert a Volume object to a domain model representation.

        Args:
            volume (Volume): The Volume object to convert.

        Returns:
            Dict: The domain model representation of the volume.
        """
        volume_dict = volume.__dict__.copy()
        volume_dict.pop('_sa_instance_state')
        volume_dict.pop('attachments')
        volume_dict.update(
            {
                'id': str(volume_dict.get('id', '')),
                'storage_id': str(volume_dict.get('storage_id', '')),
                'user_id': str(volume_dict.get('user_id', '')),
            }
        )
        return volume_dict

    @classmethod
    def to_db(cls, domain_data: Dict, orm_class: Type = Volume) -> object:
        """Convert a domain model representation to a database object.

        Args:
            domain_data (Dict): The domain model data to convert.
            orm_class (Type): The ORM class to map the data to.

        Returns:
            object: The ORM object populated with the domain data.
        """
        orm_dict = {}
        inspected_orm_class = inspect(orm_class)
        for column in list(inspected_orm_class.columns):
            column_name = column.__dict__['key']
            if not domain_data.get(column_name):
                continue
            orm_dict[column_name] = domain_data.get(column_name)
        return orm_class(**orm_dict)

    @classmethod
    def to_web(cls, volume: Volume) -> Dict:
        """Convert a Volume object to a web response representation.

        Args:
            volume (Volume): The Volume object to convert.

        Returns:
            Dict: The web response representation of the volume.
        """
        volume_dict = volume.__dict__.copy()
        volume_dict.pop('_sa_instance_state')
        attachments = []
        for attachment in volume_dict.pop('attachments', []):
            edited_attachment = attachment.__dict__.copy()
            edited_attachment.pop('_sa_instance_state')
            edited_attachment.update(
                {
                    'volume_id': str(edited_attachment.get('volume_id', '')),
                    'vm_id': str(edited_attachment.get('vm_id', '')),
                    'user_id': str(edited_attachment.get('user_id', '')),
                }
            )
            attachments.append(edited_attachment)
        volume_dict.update(
            {
                'id': str(volume_dict.get('id', '')),
                'storage_id': str((volume_dict.get('storage_id', ''))),
                'user_id': str((volume_dict.get('user_id', ''))),
                'attachments': attachments,
            }
        )
        return volume_dict
