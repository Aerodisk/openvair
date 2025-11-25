"""CRUD operations for notifications.

This module provides the `NotificationCrud` class, which is responsible for
handling CRUD operations related to notifications, including sending
notifications via the service layer.

Classes:
    - NotificationCrud: Class for managing CRUD operations related to
        notifications.
"""

from typing import Dict

from openvair.libs.log import get_logger
from openvair.modules.notification.config import API_SERVICE_LAYER_QUEUE_NAME
from openvair.libs.messaging.messaging_agents import MessagingClient
from openvair.modules.notification.service_layer import services

LOG = get_logger(__name__)


class NotificationCrud:
    """CRUD class for managing notifications."""

    def __init__(self) -> None:
        """Initialize the NotificationCrud instance.

        This constructor sets up the RPC client for communication with the
        service layer.
        """
        self.service_layer_rpc = MessagingClient(
            queue_name=API_SERVICE_LAYER_QUEUE_NAME
        )

    def send_notification(self, data: Dict) -> Dict:
        """Send a notification via the service layer.

        This method sends a notification by calling the service layer's
        `send_notification` method.

        Args:
            data (Dict): The data for the notification to send.

        Returns:
            Dict: The response from the service layer.
        """
        LOG.info('Call service layer on create notification.')
        result: Dict = self.service_layer_rpc.call(
            services.NotificationServiceLayerManager.send_notification.__name__,
            data_for_method=data,
            priority=8,
        )
        LOG.debug('Response from service layer: %s.' % result)
        return result
