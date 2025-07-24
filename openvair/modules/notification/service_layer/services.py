"""Services for the notification service layer.

This module defines the `NotificationServiceLayerManager` class, which is
responsible for handling notifications at the service layer, including
creating, sending, and updating the status of notifications.

Classes:
    - NotificationStatus: Enum class representing the status of a notification.
    - NotificationServiceLayerManager: Manager class for handling notification
        operations in the service layer.
"""

from __future__ import annotations

import datetime
from enum import Enum
from typing import TYPE_CHECKING, Dict

from sqlalchemy.exc import SQLAlchemyError

from openvair.libs.log import get_logger
from openvair.modules.base_manager import BackgroundTasks
from openvair.modules.notification import config
from openvair.libs.messaging.exceptions import (
    RpcCallException,
    RpcCallTimeoutException,
)
from openvair.modules.notification.config import (
    API_SERVICE_LAYER_QUEUE_NAME,
    SERVICE_LAYER_DOMAIN_QUEUE_NAME,
)
from openvair.libs.messaging.messaging_agents import MessagingClient
from openvair.modules.notification.domain.base import BaseNotification
from openvair.modules.notification.service_layer import unit_of_work
from openvair.modules.notification.adapters.serializer import DataSerializer

if TYPE_CHECKING:
    from openvair.modules.notification.adapters.orm import Notification

LOG = get_logger(__name__)


class NotificationStatus(Enum):
    """Enum representing the possible statuses of a notification."""

    created = 0
    sent = 1
    error = 2


class NotificationServiceLayerManager(BackgroundTasks):
    """Manager for handling notification operations in the service layer.

    This class is responsible for managing the process of creating, sending,
    and updating notifications within the service layer. It interacts with
    the domain layer and manages database transactions.

    Attributes:
        uow (NotificationSqlAlchemyUnitOfWork): The unit of work for managing
            database transactions.
        domain_rpc (Protocol): The RPC client for interacting with the domain
            layer.
        service_layer_rpc (Protocol): The RPC client for interacting with the
            service layer queue.
    """

    def __init__(self) -> None:
        """Initialize the NotificationServiceLayerManager.

        This constructor sets up the unit of work and RPC protocols for
        interacting with the domain layer and service layer queues.
        """
        super().__init__()
        self.uow = unit_of_work.NotificationSqlAlchemyUnitOfWork
        self.domain_rpc = MessagingClient(
            queue_name=SERVICE_LAYER_DOMAIN_QUEUE_NAME
        )
        self.service_layer_rpc = MessagingClient(
            queue_name=API_SERVICE_LAYER_QUEUE_NAME
        )

    def send_notification(self, data: Dict) -> Dict:
        """Create a notification, set its status, and send it to the domain.

        Args:
            data (Dict): Data for the current notification.

        Returns:
            Dict: A dictionary with notification information and the result
                status.
        """
        LOG.info(
            'Service layer start handling response on create notification.'
        )

        db_notification = DataSerializer.to_db(data)
        self._write_to_db(db_notification, NotificationStatus.created)
        self._send_notification(db_notification)

        serialized_notification = DataSerializer.to_domain(db_notification)
        LOG.info(
            'Service layer method send notification was successfully processed'
        )
        return serialized_notification

    def _send_notification(self, notification: Notification) -> None:
        """Send the notification to the domain layer.

        This method collects notification parameters and sends the incoming
        notification to the domain layer.

        Args:
            notification (Notification): The notification instance to send.
        """
        notifications_project_params = config.get_notifications_config()
        notification_dict = DataSerializer.to_domain(notification)
        notification_dict.update(notifications_project_params)

        try:
            self.domain_rpc.call(
                BaseNotification.send.__name__,
                data_for_manager=notification_dict,
                time_limit=15,
            )
            self._write_to_db(notification, NotificationStatus.sent)
        except (
            SQLAlchemyError,
            RpcCallException,
            RpcCallTimeoutException,
        ) as err:
            LOG.error(
                f'{err} - Service layer method send notification '
                'was not successfully processed'
            )
            self._write_to_db(notification, NotificationStatus.error)
            raise

    def _write_to_db(
        self, notification: Notification, status: NotificationStatus
    ) -> None:
        """Set the notification status and write it into the database.

        Args:
            notification (Notification): The notification instance to update.
            status (NotificationStatus): The new status of the notification.
        """
        LOG.info('Handling call on write notification.')
        notification.status = status.name
        notification.create_datetime = datetime.datetime.now()
        with self.uow() as uow:
            uow.notifications.add(notification)
            uow.commit()

        LOG.info(
            'Handling call on write notification was successfully processed.'
        )


if __name__ == '__main__':
    s = NotificationServiceLayerManager()
    s.send_notification(
        {
            'msg_type': 'email',
            'recipients': ['user@example.com'],
            'subject': 'string',
            'message': 'string',
        }
    )
