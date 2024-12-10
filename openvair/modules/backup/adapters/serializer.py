"""Provide classes for serializing and deserializing backuping objects

It includes a concrete implementation `DataSerializer` which provides methods
to convert backup objects to domain, database, and pydantic models.

Classes:
    DataSerializer: Concrete implementation of AbstractDataSerializer.
"""

from typing import Dict, Type

from openvair.abstracts.serializer import AbstractDataSerializer


class DataSerializer(AbstractDataSerializer):
    """Data serializer class.

    Provides methods to serialize data between different representations.

    Methods:
        to_domain: Converts data to a domain object.
        to_db: Converts data to a database object.
        to_web: Converts data to a web response object.
    """

    @classmethod
    def to_domain(cls, orm_object: object) -> Dict:  # noqa: D102 # TODO need to implement
        raise NotImplementedError

    @classmethod
    def to_db(cls, data: Dict, orm_class: Type[object]) -> object:  # noqa: D102 # TODO need to implement
        raise NotImplementedError

    @classmethod
    def to_web(cls, orm_object: object) -> Dict:  # noqa: D102 # TODO need to implement
        raise NotImplementedError
