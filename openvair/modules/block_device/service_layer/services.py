"""Module for managing the Block Devices Service Layer.

This module defines the `BlockDevicesServiceLayerManager` class, which serves as
the main entry point for handling block device-related operations in the service
layer. The class is responsible for interacting with the domain layer and the
event store to perform various tasks, such as retrieving the host IQN and
managing ISCSI sessions.

The module also includes the `ISCSIInterfaceStatus` enum, which defines the
possible status values for an ISCSI interface, and the `CreateInterfaceInfo`
namedtuple, which is used to store information about a new ISCSI interface.

Classes:
    ISCSIInterfaceStatus: Enum representing the possible status values for an
        ISCSI interface.
    CreateInterfaceInfo: Namedtuple for storing information about a new ISCSI
        interface.
    BlockDevicesServiceLayerManager: Manager class for handling block devices
        service layer operations.
"""

from __future__ import annotations

import enum
from typing import TYPE_CHECKING, Any
from collections import namedtuple

from sqlalchemy.exc import SQLAlchemyError

from openvair.libs.log import get_logger
from openvair.modules.base_manager import BackgroundTasks
from openvair.libs.messaging.exceptions import (
    RpcCallException,
    RpcCallTimeoutException,
)
from openvair.modules.block_device.config import (
    API_SERVICE_LAYER_QUEUE_NAME,
    SERVICE_LAYER_DOMAIN_QUEUE_NAME,
)
from openvair.libs.messaging.messaging_agents import MessagingClient
from openvair.modules.block_device.domain.base import (
    BaseISCSI,
    BaseFibreChannel,
)
from openvair.modules.block_device.service_layer import exceptions, unit_of_work
from openvair.modules.event_store.entrypoints.crud import EventCrud
from openvair.modules.block_device.adapters.serializer import DataSerializer

if TYPE_CHECKING:
    from uuid import UUID

    from openvair.modules.block_device.adapters.orm import ISCSIInterface

LOG = get_logger(__name__)


class ISCSIInterfaceStatus(enum.Enum):
    """Enum representing the possible status values for an ISCSI interface."""

    new = 1
    creating = 2
    available = 3
    error = 4
    deleting = 5


CreateInterfaceInfo = namedtuple(
    'CreateInterfaceInfo',
    [
        'ip',
        'inf_type',
        'port',
        'status',
    ],
)


class BlockDevicesServiceLayerManager(BackgroundTasks):
    """Manager class for handling block devices service layer operations.

    This class is responsible for coordinating the interactions between the
    service layer and the domain layer, as well as the event store, to manage
    block device-related operations.

    Attributes:
        domain_rpc (RabbitRPCClient): RPC client for communicating with the
            domain layer.
        service_layer_rpc (RabbitRPCClient): RPC client for communicating
            with the API service layer.
        uow (BlockDeviceSqlAlchemyUnitOfWork): Unit of work for managing
            database transactions.
        event_store (EventCrud): Event store for handling block device-related
            events.
    """

    def __init__(self) -> None:
        """Initialize the BlockDevicesServiceLayerManager.

        This method sets up the necessary components for the
        BlockDevicesServiceLayerManager, including the RabbitMQ RPC clients,
        the unit of work, and the event store.
        """
        super().__init__()
        self.domain_rpc = MessagingClient(
            queue_name=SERVICE_LAYER_DOMAIN_QUEUE_NAME
        )
        self.service_layer_rpc = MessagingClient(
            queue_name=API_SERVICE_LAYER_QUEUE_NAME
        )
        self.uow = unit_of_work.BlockDeviceSqlAlchemyUnitOfWork()
        self.event_store: EventCrud = EventCrud('block_devices')

    def get_host_iqn(self) -> dict:
        """Get the IQN of the host initiator.

        Returns:
            Dict: A dictionary containing the host IQN.

        Raises:
            ISCSIIqnGetException: If an error occurs while retrieving the host
                IQN.
        """
        LOG.info('Service layer start getting host IQN')
        try:
            result = self.domain_rpc.call(
                BaseISCSI.get_host_iqn.__name__,
                data_for_manager={'inf_type': 'iscsi'},
            )
        except (RpcCallException, RpcCallTimeoutException) as err:
            message = f'Error while getting host IQN: {err}'
            LOG.error(message)
            raise exceptions.ISCSIIqnGetException(message)
        else:
            return {'iqn': result}

    def get_all_sessions(self) -> list[dict[str, Any]]:
        """Gets all the ISCSI sessions from database

        Returns:
            List[Dict[str, Any]]: List of all ISCSI sessions
        """
        LOG.info('Getting all sessions from database')
        with self.uow:
            iscsi_sessions = self.uow.interfaces.get_all()
            result: list[dict[str, Any]] = [
                DataSerializer.to_web(session) for session in iscsi_sessions
            ]
            LOG.info(f'ISCSI sessions list: {result}')
        return result

    def login(self, data: dict) -> dict:
        """Logs in to the specified ISCSI block device.

        Args:
            data (Dict): Data for login, including the IP address, port, and
                user data.

        Returns:
            Dict: Result of the login operation, including the updated ISCSI
                interface information.

        Raises:
            ISCSILoginException: If an error occurs during the login process.
        """
        LOG.info('Start to login to the ISCSI block device.')

        user_data: dict = data.get('user_data', {})
        create_iface_info = CreateInterfaceInfo(
            inf_type=data.get('inf_type'),
            ip=data.get('ip'),
            port=data.get('port'),
            status=ISCSIInterfaceStatus.new.name,
        )
        db_interface: ISCSIInterface = DataSerializer.to_db(
            create_iface_info._asdict()
        )
        with self.uow:
            try:
                self.uow.interfaces.add(db_interface)
                self.uow.commit()
                message = (
                    'ISCSI interface inserted into db:'
                    f'{create_iface_info._asdict()}'
                )
                LOG.info(message)
                self.event_store.add_event(
                    str(db_interface.id),
                    user_data.get('id', ''),
                    self.login.__name__,
                    message,
                )
                # adding the ISCSI interface in database as new
                LOG.info(
                    'service layer start handling response on logging ISCSI.'
                )
                web_interface = DataSerializer.to_web(db_interface)
                LOG.debug(f'Serialized db interface for web: {web_interface}')
                # run domain logic
                result = self.domain_rpc.call(
                    BaseISCSI.login.__name__,
                    data_for_manager=web_interface,
                )
                LOG.info('Updating interface DB state on available')
                db_interface = self.uow.interfaces.get_or_fail(db_interface.id)
                db_interface.port = result.get('port', '')
                db_interface.status = ISCSIInterfaceStatus.available.name
                self.uow.commit()
                # update interface state as available
            except SQLAlchemyError as err:
                message = (
                    f'An error occurred while writing to the database {err}'
                )
                LOG.error(message)
                raise exceptions.ISCSILoginException(message)
            except (RpcCallException, RpcCallTimeoutException) as err:
                message = (
                    'An error occurred while logging in to the ISCSI block '
                    f'device: {err}.'
                )
                LOG.error(message)
                self._rollback(db_interface.id)
                raise exceptions.ISCSILoginException(message)
            else:
                message = 'Successfully logged into the ISCSI block device.'
                LOG.info(message)
                self.event_store.add_event(
                    str(db_interface.id),
                    user_data.get('id', ''),
                    self.login.__name__,
                    message,
                )

                return DataSerializer.to_web(db_interface)

    def logout(self, data: dict) -> dict:
        """Logs out from the specified ISCSI block device.

        Args:
            data (Dict): Data for logout, including the IP address and user
                data.

        Returns:
            Dict: Result of the logout operation.

        Raises:
            ISCSILogoutException: If an error occurs during the logout process.
        """
        LOG.info('Start to logging out from the ISCSI block device.')

        user_data = data.get('user_data', {})
        with self.uow:
            db_interface = self.uow.interfaces.get_by_ip(data['ip'])
            db_interface.status = ISCSIInterfaceStatus.deleting.name
            self.uow.commit()
            try:
                result: dict = self.domain_rpc.call(
                    BaseISCSI.logout.__name__,
                    data_for_manager=data,
                )
                message = 'Successfully logged out from the ISCSI block device.'
                LOG.info(message)
                self.event_store.add_event(
                    str(db_interface.id),
                    user_data.get('id', ''),
                    self.logout.__name__,
                    message,
                )
            except (RpcCallException, RpcCallTimeoutException) as err:
                message = (
                    'An error occurred while logging out from the ISCSI block'
                    f' device: {err}'
                )
                LOG.error(message)
                self.event_store.add_event(
                    str(db_interface.id),
                    user_data.get('id', ''),
                    self.logout.__name__,
                    message,
                )
                raise exceptions.ISCSILogoutException(message)
            else:
                return result
            finally:
                # deleting interface from database
                with self.uow:
                    self.uow.interfaces.delete_by_id(db_interface.id)
                    self.uow.commit()
                    message = 'ISCSI interface deleted from db'
                    LOG.info(message)
                    self.event_store.add_event(
                        str(db_interface.id),
                        user_data.get('id', ''),
                        self.logout.__name__,
                        message,
                    )

    def lip_scan(self) -> str:
        """Perform a Fibre Channel LIP (Loop Initialization Procedure) scan.

        This method is responsible for initiating a Fibre Channel LIP scan on
        the host system. It communicates with the domain layer to execute the
        LIP scan and returns the result.

        Returns:
            Dict: The result of the Fibre Channel LIP scan.

        Raises:
            FibreChannelLipScanException: If an error occurs during the LIP scan
                process.
        """
        LOG.info('Service layer starts to scan for FC host adapters')
        try:
            result = self.domain_rpc.call(
                BaseFibreChannel.lip_scan.__name__,
                data_for_manager={'inf_type': 'fibre_channel'},
            )
        except (RpcCallException, RpcCallTimeoutException) as error:
            LOG.error(error)
            raise exceptions.FibreChannelLipScanException(str(error))
        else:
            return str(result)

    def _rollback(self, interface_id: UUID) -> None:
        """Rollbacks the operation by deleting the interface record from the db.

        Args:
            interface_id (UUID): The ID of the interface to be deleted.
        """
        with self.uow:
            db_interface = self.uow.interfaces.get_or_fail(interface_id)
            if db_interface:
                self.uow.interfaces.delete_by_id(interface_id)
                self.uow.commit()
                LOG.info(
                    f'Rollback: Deleted interface {interface_id} '
                    'from the database.'
                )
            else:
                LOG.warning(
                    f'Rollback: Interface {interface_id} not found in '
                    'the database.'
                )
