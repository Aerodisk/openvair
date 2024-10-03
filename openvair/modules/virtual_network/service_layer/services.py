"""Service layer for managing virtual networks.

This module defines the `VirtualNetworkServiceLayerManager` class, which
handles various operations related to virtual networks, such as creating,
retrieving, updating, and deleting networks and their associated port groups.

Classes:
    - VirtualNetworkServiceLayerManager: A manager class responsible for
        handling virtual network operations at the service layer.

Enums:
    - VirtualNetworkStatus: Enum representing the various states of a virtual
        network.
"""

from typing import TYPE_CHECKING, Dict, Literal, Optional

from sqlalchemy.exc import SQLAlchemyError

from openvair.libs.log import get_logger
from openvair.modules.base_manager import BackgroundTasks
from openvair.libs.messaging.protocol import Protocol
from openvair.modules.virtual_network.config import (
    API_SERVICE_LAYER_QUEUE_NAME,
    SERVICE_LAYER_DOMAIN_QUEUE_NAME,
)
from openvair.modules.virtual_network.domain import base
from openvair.modules.virtual_network.entrypoints import schemas
from openvair.modules.event_store.entrypoints.crud import EventCrud
from openvair.modules.virtual_network.adapters.orm import (
    PortGroup,
    VirtualNetwork,
)
from openvair.modules.virtual_network.service_layer import unit_of_work
from openvair.modules.virtual_network.adapters.serializer import DataSerializer
from openvair.modules.virtual_network.service_layer.exceptions import (
    PortGroupException,
    VirtualNetworkAlreadyExist,
    VirtualNetworkDoesNotExist,
    DataBaseVirtualNetworkException,
)
from openvair.modules.virtual_network.domain.bridge_network.bridge_net import (
    BridgePortGroup,
)

if TYPE_CHECKING:
    from openvair.libs.messaging.rpc import RabbitRPCClient

LOG = get_logger(__name__)


class VirtualNetworkServiceLayerManager(BackgroundTasks):
    """Manager for virtual network operations in the service layer.

    This class manages virtual network operations by coordinating communication
    between the service layer, domain layer, and the database.

    Attributes:
        domain_rpc (RabbitRPCClient): The RabbitMQ client for communication with
            the domain layer.
        service_layer_rpc (RabbitRPCClient): The RabbitMQ client for
            communication with the API service layer.
        uow (SqlAlchemyUnitOfWork): The unit of work for database operations.
        event_store (EventCrud): The event store for logging operations related
            to virtual networks.
    """

    def __init__(self):
        """Initialize the VirtualNetworkServiceLayerManager."""
        super().__init__()
        self.domain_rpc: RabbitRPCClient = Protocol(client=True)(
            SERVICE_LAYER_DOMAIN_QUEUE_NAME
        )
        self.service_layer_rpc: RabbitRPCClient = Protocol(client=True)(
            API_SERVICE_LAYER_QUEUE_NAME
        )
        self.uow = unit_of_work.SqlAlchemyUnitOfWork()
        self.event_store = EventCrud('virtual_networks')

    def get_all_virtual_networks(self) -> Dict:
        """Retrieve all virtual networks from the database.

        Returns:
            Dict: A dictionary containing information about all virtual networks
        """
        LOG.info('Start getting all virtual networks from db...')
        with self.uow:
            db_networks = self.uow.virtual_networks.get_all()
            web_networks = {
                'virtual_networks': [
                    DataSerializer.to_web(db_network)
                    for db_network in db_networks
                ]
            }
        LOG.info('End of getting all virtual networks from db.')
        return web_networks

    def get_virtual_network_by_id(self, data: Dict) -> Dict:
        """Retrieve a virtual network by its ID from the database.

        Args:
            data (Dict): A dictionary containing the ID of the virtual network.

        Returns:
            Dict: Information about the virtual network.
        """
        LOG.info(f"Start getting virtual network {data.get('id')} from db...")
        vn_id = data.pop('id')
        with self.uow:
            db_network = self.uow.virtual_networks.get(vn_id)
            web_network = DataSerializer.to_web(db_network)
        LOG.info(f'End of getting virtual network {vn_id} from db.')
        return web_network

    def get_virtual_network_by_name(self, data: Dict) -> Dict:
        """Retrieve a virtual network by its name from the database.

        Args:
            data (Dict): A dictionary containing the name of the virtual
                network.

        Returns:
            Dict: Information about the virtual network.
        """
        LOG.info(
            f"Start getting virtual network {data.get('virtual_network_name')} "
            f"from db..."
        )
        vn_name = data.pop('virtual_network_name')
        with self.uow:
            db_network = self.uow.virtual_networks.get_by_name(vn_name)
            if db_network is None:
                raise VirtualNetworkDoesNotExist(vn_name)
            web_network = DataSerializer.to_web(db_network)
        LOG.info(f'End of getting virtual network {vn_name} from db.')
        return web_network

    def create_virtual_network(self, data: Dict) -> Dict:
        """Create a new virtual network.

        Args:
            data (Dict): A dictionary containing information about the virtual
                network.

        Returns:
            Dict: Information about the created virtual network.
        """
        LOG.info('Start creating virtual network...')

        user_info = data.pop('user_info')
        event_message = self.__prepare_event_message(
            user_id=user_info.get('id'),
            event=self.create_virtual_network.__name__,
        )

        db_port_groups = [
            DataSerializer.to_db(port_group, PortGroup)
            for port_group in data.pop('port_groups')
        ]
        db_network = DataSerializer.to_db(data)
        db_network.port_groups = db_port_groups

        domain_network = DataSerializer.to_domain(db_network)
        self._check_exist(domain_network)
        self.__write_into_database(db_network)

        event_message['object_id'] = db_network.id
        event_message['information'] = (
            f'Virtual network {db_network.network_name} successfully inserted '
            'into db.'
        )
        self.event_store.add_event(**event_message)

        domain_network.update({'id': str(db_network.id)})
        virsh_data = self.domain_rpc.call(
            base.BaseVirtualNetwork.create.__name__,
            data_for_manager=domain_network,
        )
        event_message['information'] = (
            f"Virtual network {domain_network.get('network_name')} "
            "successfully created."
        )
        self.event_store.add_event(**event_message)

        self._add_virsh_data_for_db_network(db_network, virsh_data)
        self.__write_into_database(db_network)
        web_network = DataSerializer.to_web(db_network)

        LOG.info('Virtual network successfully created')
        return web_network

    def delete_virtual_network(self, data: Dict) -> None:
        """Delete a virtual network.

        Args:
            data (Dict): A dictionary containing the ID of the virtual network
                to be deleted.
        """
        LOG.info('Deleting virtual network...')

        user_info = data.pop('user_info')
        vn_id = data.get('virtual_network_id')
        event_message = self.__prepare_event_message(
            user_id=user_info.get('id'),
            object_id=vn_id,
            event=self.delete_virtual_network.__name__,
        )

        with self.uow:
            db_network = self.uow.virtual_networks.get(vn_id)
            domain_network = DataSerializer.to_domain(db_network)

        LOG.info(
            'Sending request to domain layer to delete the virtual network...'
        )
        self.domain_rpc.cast(
            base.BaseVirtualNetwork.delete.__name__,
            data_for_manager=domain_network,
        )

        message = (
            f"Delete command for {domain_network.get('network_name')} was "
            "sent to domain..."
        )
        event_message['information'] = message
        LOG.info(message)
        self.event_store.add_event(**event_message)

        LOG.info('Deleting virtual network from db...')
        with self.uow:
            self.uow.virtual_networks.delete(vn_id)
            self.uow.commit()

        message = (
            f"Virtual network {domain_network.get('network_name')} deleted"
            "from db successfully"
        )
        event_message['information'] = message
        LOG.info(message)
        self.event_store.add_event(**event_message)

        LOG.info('End of deleting virtual network')

    def turn_on_virtual_network(self, data: Dict) -> None:
        """Turn on a virtual network.

        Args:
            data (Dict): A dictionary containing the ID of the virtual network
                to be turned on.
        """
        LOG.info(
            f"Turning on virtual network {data.get('virtual_network_id')}..."
        )

        vn_id = data.pop('virtual_network_id')
        self.__change_state(vn_id, 'on')

        LOG.info(f'Virtual network: {vn_id} turned on')

    def turn_off_virtual_network(self, data: Dict) -> None:
        """Turn off a virtual network.

        Args:
            data (Dict): A dictionary containing the ID of the virtual network
                to be turned off.
        """
        LOG.info(
            f"Turning off virtual network {data.get('virtual_network_id')}..."
        )

        vn_id = data.pop('virtual_network_id')
        self.__change_state(vn_id, 'off')

        LOG.info(f'Virtual network: {vn_id} turned off')

    def add_port_group(self, data: Dict) -> Dict:
        """Add a port group to a virtual network.

        Args:
            data (Dict): A dictionary containing information about the virtual
                network and the port group to be added.

        Returns:
            Dict: Information about the virtual network after adding the port
                group.
        """
        LOG.info(f"Adding port group to virtual network {data.get('vn_id')}...")

        user_info = data.pop('user_info')
        vn_id = data.pop('vn_id')
        port_group_info = data.pop('port_group_info')
        port_group_name = port_group_info.get('port_group_name')

        event_message = self.__prepare_event_message(
            user_id=user_info.get('id'),
            object_id=vn_id,
            event=self.add_port_group.__name__,
        )

        db_port_group = DataSerializer.to_db(port_group_info, PortGroup)
        domain_port_group = DataSerializer.to_domain(
            db_port_group, BridgePortGroup
        )

        with self.uow:
            db_network = self.uow.virtual_networks.get(vn_id)
            domain_network = DataSerializer.to_domain(db_network)

            for pg in domain_network.get('port_groups', []):
                if pg.get('port_group_name') == port_group_name:
                    message = (
                        f'Port group with name {port_group_name}'
                        ' already exists'
                    )
                    raise PortGroupException(message)

            message = (
                f"Port group {domain_port_group.get('port_group_name')}"
                "inserted into db."
            )
            event_message['information'] = message
            LOG.info(message)
            self.event_store.add_event(**event_message)

            virsh_data = self.domain_rpc.call(
                base.BaseVirtualNetwork.add_port_group.__name__,
                data_for_manager=domain_network,
                data_for_method=domain_port_group,
            )

            message = (
                f"Port group {domain_port_group.get('port_group_name')} was "
                f"created for network {db_network.network_name}"
            )
            event_message['information'] = message
            LOG.info(message)
            self.event_store.add_event(**event_message)

            db_network.port_groups.append(db_port_group)
            self._add_virsh_data_for_db_network(db_network, virsh_data)
            self.uow.commit()

        web_network = DataSerializer.to_web(db_network)
        LOG.info(f'Port group successfully added to virtual network {vn_id}')

        return web_network

    def delete_port_group(self, data: Dict) -> None:
        """Delete a port group from a virtual network.

        Args:
            data (Dict): A dictionary containing the ID of the virtual network
                and the name of the port group to be deleted.
        """
        LOG.info(
            f"Deleting port group from virtual network {data.get('vn_id')}..."
        )

        vn_id = data.pop('virtual_network_id')
        pg_name = data.pop('port_group_name')
        user_info = data.pop('user_info')
        event_message = self.__prepare_event_message(
            user_id=user_info.get('id'),
            object_id=vn_id,
            event=self.add_port_group.__name__,
        )

        with self.uow:
            db_network = self.uow.virtual_networks.get(vn_id)

            if len(db_network.port_groups) <= 1:
                message = (
                    f'Error while deleting port group {pg_name}: The '
                    'virtual network must contain at least one port group'
                )
                event_message['information'] = message
                self.event_store.add_event(**event_message)
                raise PortGroupException(message)

            domain_network = DataSerializer.to_domain(db_network)
            virsh_data = self.domain_rpc.call(
                base.BaseVirtualNetwork.del_port_group_by_name.__name__,
                data_for_manager=domain_network,
                data_for_method={'port_group_name': pg_name},
            )

            for pg in db_network.port_groups.copy():
                if pg.port_group_name == pg_name:
                    db_network.port_groups.remove(pg)
            self._add_virsh_data_for_db_network(db_network, virsh_data)
            self.uow.commit()

        message = (
            f'Port group {pg_name} successfully deleted from'
            f'virtual network {db_network.network_name}.'
        )
        event_message['information'] = message
        self.event_store.add_event(**event_message)
        LOG.info(message)

    def add_tag_to_port_group(self, data: Dict) -> Dict:
        """Add a tag to a port group in a virtual network.

        Args:
            data (Dict): A dictionary containing information about the virtual
                network, port group, and tag to be added.

        Returns:
            Dict: Information about the port group after adding the tag.
        """
        LOG.info('Adding tag to port group...')

        vn_id = data.pop('vn_id')
        pg_name = data.pop('pg_name')
        tag_id = data.pop('tag')
        user_info = data.pop('user_info')
        event_message = self.__prepare_event_message(
            user_id=user_info.get('id'),
            object_id=vn_id,
            event=self.add_port_group.__name__,
        )

        with self.uow:
            db_network = self.uow.virtual_networks.get(vn_id)
            domain_network = DataSerializer.to_domain(db_network)

            domain_data = self.domain_rpc.call(
                base.BaseVirtualNetwork.add_tag_to_port_group.__name__,
                data_for_manager=domain_network,
                data_for_method={'pg_name': pg_name, 'tag_id': tag_id},
            )
            virsh_data = domain_data.pop('virsh_data')
            domain_port_group = domain_data.pop('port_group')

            for port_group in db_network.port_groups:
                if port_group.port_group_name == pg_name:
                    db_network.port_groups.remove(port_group)

            db_port_group = DataSerializer.to_db(domain_port_group, PortGroup)
            db_network.port_groups.append(db_port_group)

            self._add_virsh_data_for_db_network(db_network, virsh_data)
            self.uow.commit()

        web_port_group = DataSerializer.to_web(db_port_group, schemas.PortGroup)

        message = f'Success adding tag {tag_id} to port group {pg_name}'
        event_message['information'] = message
        self.event_store.add_event(**event_message)
        LOG.info('Success adding tag to port group')
        return web_port_group

    # PROTECTED METHODS
    def _check_exist(self, domain_network: Dict) -> None:
        """Check if a network already exists in the database and in virsh.

        Args:
            domain_network (Dict): A dictionary containing information about the
                network.

        Raises:
            VirtualNetworkAlreadyExist: If the network already exists in either
                the database or in virsh.
        """
        vn_name = domain_network.get('network_name')
        LOG.info(f'Checking if network {vn_name} exists...')

        is_exist_in_db = self._check_existing_in_db(vn_name)
        is_exist_in_virsh = self.domain_rpc.call(
            base.BaseVirtualNetwork.is_exist_in_virsh.__name__,
            data_for_manager=domain_network,
        )

        msg = f'Network {vn_name} already exists'
        if is_exist_in_db and is_exist_in_virsh:
            msg += ' in DB and virsh'
            LOG.error(msg.format(vn_name=vn_name, where='DB'))
            raise VirtualNetworkAlreadyExist(msg)
        if is_exist_in_db:
            msg += ' in DB'
            LOG.error(msg.format(vn_name=vn_name, where='DB'))
            raise VirtualNetworkAlreadyExist(msg)
        if is_exist_in_virsh:
            msg += ' in virsh'
            LOG.error(msg.format(vn_name=vn_name, where='virsh'))
            raise VirtualNetworkAlreadyExist(msg)

        LOG.info(f'Network {vn_name} not exist, continue working..')

    def _check_existing_in_db(self, vn_name: str) -> bool:
        """Check if a network already exists in the database.

        Args:
            vn_name (str): The name of the network.

        Returns:
            bool: True if the network exists in the database, False otherwise.
        """
        with self.uow:
            db_network = self.uow.virtual_networks.get_by_name(vn_name)
            if db_network and db_network.network_name == vn_name:
                return True
        return False

    def _add_virsh_data_for_db_network(
        self,
        db_network: VirtualNetwork,
        data: Dict,
    ) -> None:
        """Update a database network object with data from virsh.

        Args:
            db_network (VirtualNetwork): The database network object to update.
            data (Dict): The data from virsh.
        """
        db_network.virsh_xml = data.pop('virsh_xml')
        db_network.state = data.pop('state')
        db_network.autostart = data.pop('autostart')
        db_network.persistent = data.pop('persistent')

    # PRIVATE METHODS
    def __write_into_database(self, db_network: VirtualNetwork) -> None:
        """Write network information into the database.

        Args:
            db_network (VirtualNetwork): The network object to be written into
                the database.

        Raises:
            DataBaseVirtualNetworkException: If an error occurs while writing
                the network into the database.
        """
        network_name = db_network.network_name
        LOG.info(f'Writing network {network_name} into database...')
        try:
            with self.uow:
                self.uow.virtual_networks.add(db_network)
                self.uow.commit()
            LOG.info(f'Network {network_name} written in database')
        except SQLAlchemyError as err:
            msg = f'SQLAlchemyError {err}. network_name: {network_name}'
            LOG.error(msg)
            raise DataBaseVirtualNetworkException(msg)

    def __change_state(
        self,
        vn_id: str,
        action: Literal['on', 'off'],
    ) -> None:
        """Change the state of a virtual network.

        Args:
            vn_id: The ID of the virtual network.
            action: The action to be performed ('on' or 'off').
        """
        with self.uow:
            db_network = self.uow.virtual_networks.get(vn_id)
            domain_network = DataSerializer.to_domain(db_network)

            if action == 'on':
                db_network.state = self.domain_rpc.call(
                    base.BaseVirtualNetwork.enable.__name__,
                    data_for_manager=domain_network,
                )

            elif action == 'off':
                db_network.state = self.domain_rpc.call(
                    base.BaseVirtualNetwork.disable.__name__,
                    data_for_manager=domain_network,
                )

            self.uow.commit()

    def __prepare_event_message(
        self,
        user_id: Optional[str] = None,
        object_id: Optional[str] = None,
        event: Optional[str] = None,
    ) -> Dict:
        """Prepare an event message dictionary.

        Args:
            user_id (Optional[str]): The ID of the user triggering the event.
            object_id (Optional[str]): The ID of the object involved in the
                event.
            event (Optional[str]): The name of the event.

        Returns:
            Dict: The prepared event message dictionary.
        """
        return {
            'user_id': user_id,
            'object_id': object_id,
            'event': event,
            'information': None,
        }
