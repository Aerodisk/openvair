from typing import Dict

from openvair.config import RPC_QUEUES, data, get_default_session_factory

API_SERVICE_LAYER_QUEUE_NAME: str = RPC_QUEUES.Notification.SERVICE_LAYER
SERVICE_LAYER_DOMAIN_QUEUE_NAME: str = RPC_QUEUES.Notification.DOMAIN_LAYER

DEFAULT_SESSION_FACTORY = get_default_session_factory()


def get_notifications_config() -> Dict:
    """Getting notifications data from project config"""
    notification_config_data: Dict = data['notifications']
    return notification_config_data
