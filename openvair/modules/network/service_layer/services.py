"""Service layer for managing network interfaces and bridges.

This module defines the `NetworkServiceLayerManager` class, which provides
methods for managing network interfaces and bridges. It handles operations
such as creating, deleting, and updating network interfaces, as well as
interfacing with the domain layer and the database.

Classes:
    InterfaceStatus: Enumeration for interface status.
    NetworkServiceLayerManager: Manager class for handling network-related
        operations in the service layer.
"""

from __future__ import annotations

import enum
from typing import Dict, List, Optional, cast
from collections import namedtuple

from sqlalchemy.exc import SQLAlchemyError

from openvair.libs.log import get_logger
from openvair.modules.network import utils
from openvair.modules.base_manager import BackgroundTasks, periodic_task
from openvair.modules.network.config import (
    API_SERVICE_LAYER_QUEUE_NAME,
    SERVICE_LAYER_DOMAIN_QUEUE_NAME,
)
from openvair.modules.network.adapters import orm
from openvair.libs.messaging.exceptions import (
    RpcCallException,
    RpcCallTimeoutException,
)
from openvair.modules.network.domain.base import BaseBridge, BaseInterface
from openvair.modules.network.service_layer import exceptions, unit_of_work
from openvair.libs.messaging.messaging_agents import MessagingClient
from openvair.modules.network.adapters.serializer import DataSerializer
from openvair.modules.event_store.entrypoints.crud import EventCrud

LOG = get_logger(__name__)

CreateInterfaceInfo = namedtuple(
    'CreateInterfaceInfo',
    [
        'name',
        'mac',
        'ip',
        'netmask',
        'gateway',
        'inf_type',
        'power_state',
        'status',
    ],
)


class InterfaceStatus(enum.Enum):
    """Enumeration for interface status.fastork interfaces,

    including 'new', 'creating', 'available', 'error', and 'deleting'.
    """

    new = 1
    creating = 2
    available = 3
    error = 4
    deleting = 5


class NetworkServiceLayerManager(BackgroundTasks):
    """Manager for handling network operations in the service layer.

    This class is responsible for managing network interfaces and bridges,
    including operations such as creating, deleting, updating, and monitoring
    network interfaces and bridges. It interacts with the domain layer, the
    database, and external services.

    Attributes:
        domain_rpc (Protocol): RPC protocol for communicating with the domain
            layer.
        service_layer_rpc (Protocol): RPC protocol for communicating within the
            service layer.
        uow (NetworkSqlAlchemyUnitOfWork): Unit of work instance for managing
            database transactions.
        event_store (EventCrud): Event store for logging events related to
            network operations.
    """

    def __init__(self) -> None:
        """Initialize the NetworkServiceLayerManager.

        This constructor sets up the necessary components for the
        NetworkServiceLayerManager, including initializing the unit of work for
        SQLAlchemy interactions, setting up RPC protocols, and creating an event
        store.
        """
        super(NetworkServiceLayerManager, self).__init__()
        self.domain_rpc = MessagingClient(
            queue_name=SERVICE_LAYER_DOMAIN_QUEUE_NAME
        )
        self.service_layer_rpc = MessagingClient(
            queue_name=API_SERVICE_LAYER_QUEUE_NAME
        )
        self.uow = unit_of_work.NetworkSqlAlchemyUnitOfWork
        self.event_store = EventCrud('networks')

    def get_all_interfaces(
        self,
        data: Dict,
    ) -> List:
        """Retrieve all network interfaces from the database.

        This method retrieves all network interfaces from the database and
        optionally filters out specific interfaces.

        Args:
            data (Dict): A dictionary containing the Boolean variable:
                - is_need_filter (Optional[bool]): Flag indicating whether to
                    apply filtering to the interfaces. Defaults to False.

        Returns:
            List: A list of serialized dictionaries representing the
                interfaces' data.
        """
        LOG.info('Start getting all interfaces from db.')
        is_need_filter = data.pop('is_need_filter', None)
        filterable_ifaces_names = ['lo']
        with self.uow() as uow:
            web_interfaces = []
            db_interfaces = uow.interfaces.get_all()
            for db_iface in db_interfaces:
                if not (
                    is_need_filter and db_iface.name in filterable_ifaces_names
                ):
                    web_interface = DataSerializer.to_web(db_iface)
                    web_interfaces.append(web_interface)
        return web_interfaces

    def get_interface(self, data: Dict) -> Dict:
        """Retrieve a network interface by its ID.

        This method retrieves a network interface from the database based on
        its ID.

        Args:
            data (Dict): A dictionary containing the interface ID.

        Raises:
            exceptions.UnexpectedDataArguments: If the interface ID is not
                provided.

        Returns:
            Dict: A serialized dictionary representing the interface's data.
        """
        LOG.info('Service layer start handling response on get interface.')
        iface_id = data.pop('iface_id', None)
        LOG.debug('Get interface id from request: %s.' % iface_id)
        if not iface_id:
            message = (
                f'Incorrect arguments were received '
                f'in the request get interface: {data}.'
            )
            LOG.error(message)
            raise exceptions.UnexpectedDataArguments(message)
        with self.uow() as uow:
            db_iface = uow.interfaces.get_or_fail(iface_id)
            web_iface = DataSerializer.to_web(db_iface)
            LOG.debug('Got interface from db: %s.' % web_iface)
        LOG.info(
            'Service layer method get interface was successfully processed'
        )
        return web_iface

    def get_bridges_list(self, data: Dict) -> List[Dict]:
        """Retrieve the list of network bridges.

        This method retrieves a list of network bridges based on the operating
        system type.

        Args:
            data (Dict): A dictionary containing inf_type and
                network_config_manager info

        Returns:
            List: A list of network bridges.
        """
        LOG.info('Start getting all network bridges')
        return list(
            self.domain_rpc.call(
                BaseBridge.get_bridges_list.__name__,
                data_for_manager=data,
            )
        )

    def create_bridge(self, data: Dict) -> Dict:
        """Create a new network bridge.

        This method creates a new network bridge in the database, sets its
        status to 'new', and initiates the creation process in the domain layer.

        Args:
            data (Dict): A dictionary containing information about the new
                network bridge.

        Raises:
            exceptions.InterfaceInsertionError: If the bridge could not be
                inserted into the database.

        Returns:
            Dict: A serialized dictionary representing the created bridge's
                data.
        """
        self._check_existance_and_port_compabilities(data)
        create_iface_info = self._validate_create_interface_info(data)
        try:
            web_iface = self._create_interface_in_db(
                create_iface_info._asdict()
            )
        except SQLAlchemyError as e:
            message = f'Failed to create interface in DB: {e}.'
            LOG.error(message)
            raise exceptions.InterfaceInsertionError(message)

        data.update({'iface_id': web_iface.get('id', '')})
        self.service_layer_rpc.cast(
            self._create_bridge.__name__, data_for_method=data
        )
        LOG.info('Service layer start creating bridge.')
        return web_iface

    def delete_bridge(self, data: Dict) -> Dict:
        """Delete a network bridge.

        This method deletes a network bridge from the database, sets its status
        to 'deleting', and initiates the deletion process in the domain layer.

        Args:
            data (Dict): A dictionary containing information about the bridge
                to delete.

        Raises:
            exceptions.UnexpectedDataArguments: If the interface ID is not
                provided.
            exceptions.InterfaceDeletingError: If an error occurs during
                deletion.

        Returns:
            Dict: A serialized dictionary representing the deleted bridge's
                data.
        """
        LOG.info('Start deleting a network bridge')
        iface_id = data.get('id')
        if not iface_id:
            message = 'Interface id was not received.'
            LOG.error(message)
            raise exceptions.UnexpectedDataArguments(message)

        with self.uow() as uow:
            db_iface = uow.interfaces.get_or_fail(iface_id)
            data['name'] = db_iface.name
            try:
                db_iface.status = InterfaceStatus.deleting.name
                uow.commit()
                serialized_iface = DataSerializer.to_web(db_iface)
            except SQLAlchemyError as e:
                message = f'Failed to delete interface from db: {e}.'
                LOG.error(message)
                raise exceptions.InterfaceDeletingError(message)

        self.service_layer_rpc.cast(
            self._delete_bridge.__name__, data_for_method=data
        )

        return serialized_iface

    def turn_on(self, data: Dict) -> None:
        """Turn on the specified network interface.

        This method retrieves the specified network interface from the
        database, converts it to the domain format, and sends a command to
        the domain layer to turn on the interface.

        Args:
            data (Dict): A dictionary containing the interface details. The key
                'name' is expected to hold the name of the interface to be
                turned on.
        """
        LOG.info('Start service layer call for turning on interface:')
        iface_name = data.get('name', '')
        LOG.info(f'Interface name: {iface_name}')

        with self.uow() as uow:
            db_iface = uow.interfaces.get_by_name(iface_name)
            if not db_iface:
                message = (f'Error while turning on interface: '
                           f'interface {iface_name} not found in DB.')
                LOG.error(message)
                raise exceptions.InterfaceNotFoundError(message)
            domain_iface = DataSerializer.to_domain(db_iface)

        LOG.info('Sending enable interface command to domain layer...')
        self.domain_rpc.cast(
            BaseInterface.enable.__name__,
            data_for_manager=domain_iface,
        )
        LOG.info('Enable command was send success')

        LOG.info(
            f'End service layer call for turning on interface: {iface_name}'
        )

    def turn_off(self, data: Dict) -> None:
        """Turn off the specified network interface.

        This method retrieves the specified network interface from the
        database, converts it to the domain format, and sends a command to
        the domain layer to turn off the interface.

        Args:
            data (Dict): A dictionary containing the interface details. The key
                'name' is expected to hold the name of the interface to be
                turned off.
        """
        LOG.info('Start service layer call for turning off interface:')
        iface_name = data.get('name', '')
        LOG.info(f'Interface name: {iface_name}')

        LOG.info('Sending disable interface command to domain layer...')
        with self.uow() as uow:
            db_iface = uow.interfaces.get_by_name(iface_name)
            if not db_iface:
                message = (f'Error while turning off interface: '
                           f'interface {iface_name} not found in DB.')
                LOG.error(message)
                raise exceptions.InterfaceNotFoundError(message)
            domain_iface = DataSerializer.to_domain(db_iface)

        self.domain_rpc.cast(
            BaseInterface.disable.__name__,
            data_for_manager=domain_iface,
        )
        LOG.info('Disable command was send success')

        LOG.info(
            f'End service layer call for turning off interface: {iface_name}'
        )

    def _create_bridge(self, data: Dict) -> None:
        """Helper method to create a bridge.

        This method validates the provided data, sets the interface status
        to 'creating' in the database, and calls the domain layer to create
        the bridge. If successful, the status is updated to 'available';
        otherwise, it is set to 'error'.

        Args:
            data (Dict): A dictionary containing information about the new
                network bridge.

        Raises:
            exceptions.CreateInterfaceDataException: If the interface ID is not
                provided.
            exceptions.InterfaceInsertionError: If an error occurs during the
                RPC call to the domain layer.
        """
        LOG.info('Start casting a new network bridge creation')
        user_info = data.pop('user_info', {})
        user_id = user_info.get('id', '')
        iface_id = data.pop('iface_id', None)

        if not iface_id:
            message = 'Interface id was not received.'
            LOG.error(message)
            raise exceptions.CreateInterfaceDataException(message)

        with self.uow() as uow:
            db_iface = uow.interfaces.get_or_fail(iface_id)
            LOG.info("Changing interface state on 'new'")
            # write a new state in database
            db_iface.status = InterfaceStatus.creating.name
            uow.commit()

        with self.uow() as uow:
            db_iface = uow.interfaces.get_or_fail(iface_id)
            try:
                # Actually create a new bridge
                LOG.info('Start calling domain layer to create a new bridge.')
                result = self.domain_rpc.call(
                    BaseBridge.create.__name__,
                    data_for_manager=data,
                    data_for_method=data,
                )
                LOG.info('Result of rpc call to domain: %s.' % result)
                # Set state as available
                db_iface.status = InterfaceStatus.available.name
                LOG.info(
                    'Interface state was updated on %s.'
                    % InterfaceStatus.available.name
                )

                self.event_store.add_event(
                    iface_id,
                    user_id,
                    self._create_bridge.__name__,
                    'Interface created successfully',
                )
            except (RpcCallException, RpcCallTimeoutException) as err:
                message = (
                    f'An error occurred when calling the '
                    f'domain layer while creating a new bridge: {err!s}'
                )
                LOG.error(message)
                db_iface.status = InterfaceStatus.error.name
                self.event_store.add_event(
                    iface_id, user_id, self._create_bridge.__name__, message
                )
                raise exceptions.InterfaceInsertionError(message)
            finally:
                uow.commit()

    def _delete_bridge(self, data: Dict) -> None:
        """Helper method to delete a network bridge.

        This method sends a command to the domain layer to delete the specified
        network bridge and updates the database accordingly.

        Args:
            data (Dict): A dictionary containing information about the bridge
                to delete.

        Raises:
            exceptions.InterfaceDeletingError: If an error occurs during the
                RPC call to the domain layer.
        """
        user_info = data.get('user_info', {})
        user_id = user_info.get('id', '')
        iface_id = data.get('id', '')

        with self.uow() as uow:
            db_iface = uow.interfaces.get_or_fail(iface_id)
            try:
                self.domain_rpc.call(
                    BaseBridge.delete.__name__,
                    data_for_manager=data,
                )
                self.event_store.add_event(
                    iface_id,
                    user_id,
                    self._delete_bridge.__name__,
                    'Bridge was deleted successfully',
                )
            except (RpcCallException, RpcCallTimeoutException) as err:
                message = (
                    f'An error occurred when calling the '
                    f'domain layer while deleting the bridge: {err!s}'
                )
                db_iface.status = InterfaceStatus.error.name
                LOG.error(message)
                self.event_store.add_event(
                    iface_id, user_id, self._delete_bridge.__name__, message
                )
                raise exceptions.InterfaceDeletingError(message)
            finally:
                uow.commit()
                try:
                    self._delete_interface_from_db(data)
                except SQLAlchemyError as e:
                    message = f'Failed to delete interface from DB: {e}.'
                    LOG.error(message)

    def _edit_interface_in_db(self, data: Dict) -> Dict:
        """Edit a network interface and its extra specs in the database.

        This method updates the specified network interface and its extra specs
        in the database based on the provided data.

        Args:
            data (Dict): A dictionary containing the interface's data. The key
                'name' is required to fetch the interface from the database.

        Raises:
            exceptions.InterfaceNotFoundError: If the interface is not found in
                the database.

        Returns:
            Dict: A serialized dictionary representing the updated interface's
                data.
        """
        LOG.info('Service layer start handling response on edit interface.')
        interface_name = data.get('name', '')
        with self.uow() as uow:
            db_interface = uow.interfaces.get_by_name(interface_name)
            if not db_interface:
                message = (
                    'Interface with name %s is not found in DB.'
                    % interface_name
                )
                LOG.error(message)
                raise exceptions.InterfaceNotFoundError(message)

            for attribute in [
                'name',
                'mac',
                'ip',
                'netmask',
                'gateway',
                'mtu',
                'speed',
                'inf_type',
                'power_state',
                'status',
            ]:
                attribute_value = data.get(
                    attribute, getattr(db_interface, attribute)
                )
                setattr(db_interface, attribute, attribute_value)

            specs = data.get('specs', {})
            self._update_extra_specs(db_interface, specs)

            uow.interfaces.add(db_interface)
            uow.commit()

            return DataSerializer.to_web(db_interface)

    def _check_existance_and_port_compabilities(self, data: Dict) -> None:
        interfaces = self.get_all_interfaces(data)
        if data['name'] in [bridge['name'] for bridge in interfaces]:
            error = exceptions.InterfaceAlreadyExistException(data['name'])
            LOG.error(error)
            raise error

        ovs_bridges = self.get_bridges_list(data)
        for iface in data.get('interfaces', []):
            if iface['name'] in [bridge['ifname'] for bridge in ovs_bridges]:
                raise exceptions.NestedOVSBridgeNotAllowedError(iface['name'])

    def _create_interface_in_db(self, data: Dict) -> Dict:
        """Create a new network interface in the database.

        This protected method is used to create a new network interface in the
        database based on the provided data. It is typically called during
        synchronization when an interface does not already exist in the
        database.

        Args:
            data (Dict): A dictionary containing the interface's data.

        Returns:
            Dict: A serialized dictionary representing the created interface's
                data.
        """
        LOG.info('Service layer start handling response on create interface.')
        with self.uow() as uow:
            db_interface = cast(orm.Interface, DataSerializer.to_db(data))
            for key, value in data.get('specs', {}).items():
                spec = {
                    'key': key,
                    'value': value,
                    'interface_id': db_interface.id,
                }
                db_interface.extra_specs.append(
                    cast(
                        orm.InterfaceExtraSpec,
                        DataSerializer.to_db(spec, orm.InterfaceExtraSpec),
                    )
                )
            uow.interfaces.add(db_interface)
            uow.commit()
            LOG.info('Interface inserted into db: %s.' % db_interface)

        web_interface = DataSerializer.to_web(db_interface)
        LOG.debug('Serialized db interface for web: %s.' % web_interface)
        LOG.info(
            'Service layer method create interface was successfully processed'
        )
        return web_interface

    def _delete_interface_from_db(self, data: Dict) -> None:
        """Delete a network interface and its extra specs from the database.

        This protected method deletes a network interface and its extra specs
        from the database based on the provided data.

        Args:
            data (Dict): A dictionary containing the interface's data. The key
                'id' is required to identify the interface to delete.

        Raises:
            exceptions.InterfaceNotFoundError: If the interface is not found in
                the database.
        """
        LOG.info('Service layer start handling response on delete interface.')
        interface_id = data.get('id', '')
        with self.uow() as uow:
            db_interface = uow.interfaces.get_or_fail(interface_id)
            if not db_interface:
                message = (
                    'Interface with id %s is not found in DB.' % interface_id
                )
                LOG.error(message)
                raise exceptions.InterfaceNotFoundError(message)

            domain_interface = DataSerializer.to_domain(db_interface)
            LOG.debug('Got interface: %s from db.' % domain_interface)
            uow.interfaces.delete(db_interface)
            LOG.info('Interface: %s deleted from db.' % interface_id)
            uow.commit()
        LOG.info(
            'Service layer method delete interface was successfully processed'
        )

    @staticmethod
    def _validate_create_interface_info(data: Dict) -> CreateInterfaceInfo:
        """Validate and create a CreateInterfaceInfo object.

        This method validates the provided data and returns a
        CreateInterfaceInfo object representing the new network interface.

        Args:
            data (Dict): A dictionary containing information about the new
                network interface.

        Raises:
            exceptions.UnexpectedDataArguments: If the provided data is invalid.

        Returns:
            CreateInterfaceInfo: An object containing validated interface data.
        """
        LOG.info('Start creating a new network bridge')
        # write new interface data into database
        iface_name = data.get('name')
        iface_ip = data.get('ip')

        if not iface_name:
            message = (
                f'Incorrect arguments were received '
                f'in the request create interface: {data}.'
            )
            LOG.error(message)
            raise exceptions.UnexpectedDataArguments(message)

        return CreateInterfaceInfo(
            name=iface_name,
            mac='',
            ip=iface_ip,
            netmask=None,
            gateway='',
            inf_type='',
            power_state='DOWN',
            status=InterfaceStatus.new.name,
        )

    @staticmethod
    def _update_extra_specs(
        db_interface: orm.Interface,
        specs: Dict,
    ) -> None:
        """Update extra specifications for a network interface in the database.

        This method updates the extra specifications for the specified network
        interface in the database, adding new specs, updating existing ones,
        and removing unnecessary specs.

        Args:
            db_interface (orm.Interface): The database interface object to
                update.
            specs (orm.InterfaceExtraSpec): A dictionary containing the
                specifications to update.
        """
        # Check existing extra_specs and update values
        for key, value in specs.items():
            existing_spec = next(
                (spec for spec in db_interface.extra_specs if spec.key == key),
                None,
            )
            if existing_spec:
                existing_spec.value = value
            else:
                # Create a new entry
                db_interface.extra_specs.append(
                    orm.InterfaceExtraSpec(key=key, value=value)
                )

        # Removing unnecessary entries
        # Update extra_specs in-place using a slice[:] to maintain the
        # reference. This efficiently modifies the list contents without
        # creating a new object.
        db_interface.extra_specs[:] = [
            spec for spec in db_interface.extra_specs if spec.key in specs
        ]

    @periodic_task(interval=10)
    def monitoring(self) -> None:  # noqa: C901 because all checking is needed; TODO: refactor to multiple methods
        """Monitor and synchronize network interfaces with the system.

        This periodic task refreshes the state of all network interfaces in the
        database with data retrieved from the operating system. It ensures that
        the database remains consistent with the actual state of the system's
        network interfaces.
        """
        LOG.info('Start monitoring')
        interfaces_from_os = {
            inf['name']: inf for inf in utils.InterfacesFromSystem().get_all()
        }

        LOG.debug('Got interfaces from system %s' % interfaces_from_os)
        with self.uow() as uow:
            db_interfaces = [
                iface.name for iface in uow.interfaces.get_all()
            ]
            LOG.debug('Got interfaces from db %s' % db_interfaces)

        for (os_iface_name), os_iface_data in interfaces_from_os.items():
            with self.uow() as uow:
                db_iface_now = uow.interfaces.get_by_name(os_iface_name)
                db_interface = self.__synchronize_os_to_db_info(
                    os_iface_data,
                    db_iface_now,
                )
                db_interface.status = InterfaceStatus.available.name
                uow.interfaces.add(db_interface)
                if os_iface_name in db_interfaces:
                    db_interfaces.remove(os_iface_name)
                uow.commit()

        prefixes_to_delete = ['vnet', 'veth']
        for db_iface_name in db_interfaces:
            with self.uow() as uow:
                db_iface = uow.interfaces.get_by_name(db_iface_name)
                if db_iface:
                    if db_iface_name.startswith('ovs-system') or any(
                        db_iface_name.startswith(prefix) for prefix
                        in prefixes_to_delete
                    ):
                        uow.interfaces.delete(db_iface)
                    # Set the status to 'error' for all other interfaces
                    else:
                        LOG.info(
                            f'Interface {db_iface_name!r} not found in os. '
                            f'Setting status to error for '
                            f'interface {db_iface!r}.'
                        )
                        db_iface.status = InterfaceStatus.error.name
                    uow.commit()

        LOG.info('Stop monitoring')

    def __synchronize_os_to_db_info(
        self,
        os_iface: Dict,
        db_iface: Optional[orm.Interface],
    ) -> orm.Interface:
        """Synchronize the OS interface data with the database.

        This method compares the interface data from the operating system with
        the data in the database and updates the database accordingly. If the
        interface does not exist in the database, it is created.

        Args:
            os_iface (Dict): A dictionary containing the interface data from
                the operating system.
            db_iface (orm.Interface): The corresponding database interface
                object, if it exists.

        Returns:
            orm.Interface: The updated or created database interface object.
        """
        os_iface_name = os_iface.get('name')
        if db_iface is None:
            LOG.warning(
                f'Interface {os_iface_name} not found in db. Trying to '
                'synchronize...'
            )
            db_iface = cast(orm.Interface, DataSerializer.to_db(os_iface))
            LOG.info(f'Interface {os_iface_name} successfully prepared for db')
        else:
            self._update_extra_specs(db_iface, os_iface.get('extra_specs', {}))

        for attribute in CreateInterfaceInfo._fields:
            attribute_value = os_iface.get(attribute)
            setattr(db_iface, attribute, attribute_value)

        return db_iface
