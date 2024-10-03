"""Data serialization for the virtual network adapter.

This module provides the `DataSerializer` class for converting data between
database, domain, and web representations.

Classes:
    - AbstractDataSerializer: Abstract base class for data serializers.
    - DataSerializer: Implementation of a data serializer.
"""

import abc
import json
from typing import Dict, Type, Union

from sqlalchemy import inspect as orm_inspect

from openvair.libs.log import get_logger
from openvair.modules.virtual_network.adapters import orm as db
from openvair.modules.virtual_network.entrypoints import schemas as web
from openvair.modules.virtual_network.domain.bridge_network.bridge_net import (
    BridgeNetwork,
    BridgePortGroup,
)

LOG = get_logger(__name__)


class AbstractDataSerializer(metaclass=abc.ABCMeta):
    """Abstract base class for data serializers."""

    @classmethod
    @abc.abstractmethod
    def to_domain(
        cls,
        instance: Union[db.VirtualNetwork, db.PortGroup],
        domain_class: Type,
    ) -> Dict:
        """Converts data to a domain object."""
        ...

    @classmethod
    @abc.abstractmethod
    def to_db(
        cls,
        data: Dict,
        orm_class: Type,
    ) -> Union[db.VirtualNetwork, db.PortGroup]:
        """Converts data to a database object."""
        ...

    @classmethod
    @abc.abstractmethod
    def to_web(
        cls,
        instance: Union[db.VirtualNetwork, db.PortGroup],
        web_class: Type,
    ) -> Dict:
        """Converts data to a web response object."""
        ...


class DataSerializer(AbstractDataSerializer):
    """Data serializer class.

    Provides methods to serialize data between different representations.

    Methods:
        to_domain: Converts data to a domain object.
        to_db: Converts data to a database object.
        to_web: Converts data to a web response object.
    """

    @classmethod
    def to_domain(
        cls,
        instance: Union[db.VirtualNetwork, db.PortGroup],
        domain_class: Type = BridgeNetwork,
    ) -> Dict:
        """Converts data to a domain object.

        Args:
            instance (Union[db.VirtualNetwork, db.PortGroup]): The data instance
                to convert.
            domain_class (Type): The domain class to convert to. Defaults to
                BridgeNetwork.

        Returns:
            Dict: The domain object.
        """
        LOG.info('Converting data to domain object...')

        orm_obj_dict = instance.__dict__.copy()
        orm_obj_dict.pop('_sa_instance_state')
        orm_port_groups = orm_obj_dict.get('port_groups')
        if orm_port_groups:
            orm_obj_dict.update(
                {
                    'port_groups': [
                        cls.to_domain(port_group, BridgePortGroup)
                        for port_group in orm_port_groups
                    ]
                }
            )
        domain_object = domain_class(**orm_obj_dict)
        domain_dict = domain_object.as_dict()

        LOG.info('Data success converted to domain object.')
        return domain_dict

    @classmethod
    def to_db(
        cls,
        data: Dict,
        orm_class: Type = db.VirtualNetwork,
    ) -> Union[db.VirtualNetwork, db.PortGroup]:
        """Converts data to a database object.

        Args:
            data (Dict): The data to convert.
            orm_class (Type): The ORM class to convert to. Defaults to
                db.VirtualNetwork.

        Returns:
            Union[db.VirtualNetwork, db.PortGroup]: The database object.
        """
        LOG.info('Converting data to db object...')

        orm_dict = {}
        inspected_orm_class = orm_inspect(orm_class)
        for column in list(inspected_orm_class.columns):
            column_name = column.__dict__['key']
            orm_dict[column_name] = data.get(column_name)

        LOG.info('Data success converted to db object.')
        return orm_class(**orm_dict)

    @classmethod
    def to_web(
        cls,
        instance: Union[db.VirtualNetwork, db.PortGroup],
        web_class: Type = web.VirtualNetworkResponse,
    ) -> Dict:
        """Converts data to a web response object.

        Args:
            instance (Union[db.VirtualNetwork, db.PortGroup]): The data instance
                to convert.
            web_class (Type): The web response class to convert to. Defaults to
                web.VirtualNetworkResponse.

        Returns:
            Dict: The web response object.
        """
        LOG.info('Converting data to web json serializable object...')

        pydantic_model = web_class.from_orm(instance)
        result_web_info = json.loads(pydantic_model.json())

        LOG.info('Data success converted to web json serializable object.')
        return result_web_info
