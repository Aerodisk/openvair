"""CRUD operations for the template API.

This module provides the TemplateCrud class for handling template-related
operations via RPC communication with the service layer.

Classes:
    - TemplateCrud: Handles interactions with the service layer for templates.

Dependencies:
    - MessagingClient: Facilitates RPC communication.
    - API_SERVICE_LAYER_QUEUE_NAME: Defines the queue for API-service
        communication.
"""

from openvair.libs.log import get_logger
from openvair.modules.template.config import API_SERVICE_LAYER_QUEUE_NAME
from openvair.libs.messaging.messaging_agents import MessagingClient

LOG = get_logger(__name__)


class TemplateCrud:
    """Handles template-related API operations.

    This class provides methods for interacting with the service layer via RPC.

    Attributes:
        service_layer_rpc (MessagingClient): RPC client for sending requests
            to the service layer.
    """

    def __init__(self) -> None:
        """Initializes the TemplateCrud service.

        Sets up an RPC client for communication with the service layer.
        """
        self.service_layer_rpc = MessagingClient(
            queue_name=API_SERVICE_LAYER_QUEUE_NAME
        )
