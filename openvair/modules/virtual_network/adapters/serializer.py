"""Provide classes for serializing and deserializing VirtualNetworks objects

It includes a concrete implementation `DataSerializer` which provides methods
to convert VirtualNetworks and PortGroup objects to domain, database,
and web-friendly dictionaries.

Classes:
    DataSerializer: Concrete implementation of AbstractDataSerializer.
"""

import json
from typing import Dict, Type, Union, cast

from pydantic import BaseModel
from sqlalchemy import inspect
from sqlalchemy.orm.mapper import Mapper

from openvair.libs.log import get_logger
from openvair.abstracts.serializer import AbstractDataSerializer
from openvair.modules.virtual_network.adapters import orm as db
from openvair.modules.virtual_network.entrypoints import schemas as web
from openvair.modules.virtual_network.domain.bridge_network.bridge_net import (
    BridgeNetwork,
    BridgePortGroup,
)

LOG = get_logger(__name__)


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
        orm_object: Union[db.VirtualNetwork, db.PortGroup],
        domain_class: Type = BridgeNetwork,
    ) -> Dict:
        """Converts data to a domain object.

        Args:
            orm_object (Union[db.VirtualNetwork, db.PortGroup]): The data
                instance to convert.
            domain_class (Type): The domain class to convert to. Defaults to
                BridgeNetwork.

        Returns:
            Dict: The domain object.
        """
        LOG.info('Converting data to domain object...')

        orm_obj_dict = orm_object.__dict__.copy()
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
        domain_dict: Dict = domain_object.as_dict()

        LOG.info('Data success converted to domain object.')
        return domain_dict

    @classmethod
    def to_db(
        cls,
        data: Dict,
        orm_class: Union[
            Type[db.VirtualNetwork],
            Type[db.PortGroup],
        ] = db.VirtualNetwork,
    ) -> Union[
        db.VirtualNetwork,
        db.PortGroup,
    ]:
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
        inspected_orm_class = cast(Mapper, inspect(orm_class))
        for column in list(inspected_orm_class.columns):
            column_name = column.__dict__['key']
            orm_dict[column_name] = data.get(column_name)

        LOG.info('Data success converted to db object.')
        return orm_class(**orm_dict)

    @classmethod
    def to_web(
        cls,
        orm_object: Union[db.VirtualNetwork, db.PortGroup],
        web_class: Type[BaseModel] = web.VirtualNetworkResponse,
    ) -> Dict:
        """Converts data to a web response object.

        Args:
            orm_object (Union[db.VirtualNetwork, db.PortGroup]): The data
                instance to convert.
            web_class (Type): The web response class to convert to. Defaults to
                web.VirtualNetworkResponse.

        Returns:
            Dict: The web response object.
        """
        LOG.info('Converting data to web json serializable object...')

        pydantic_model = web_class.model_validate(orm_object)
        result_web_info: Dict = json.loads(pydantic_model.model_dump_json())

        LOG.info('Data success converted to web json serializable object.')
        return result_web_info
