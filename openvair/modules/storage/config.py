from pathlib import Path

from openvair import config
from openvair.config import RPC_QUEUES, get_default_session_factory

STORAGE_DATA = Path(config.data['storage'].get('data_path', ''))
API_SERVICE_LAYER_QUEUE_NAME: str = RPC_QUEUES.Storage.SERVICE_LAYER
SERVICE_LAYER_DOMAIN_QUEUE_NAME: str = RPC_QUEUES.Storage.DOMAIN_LAYER

DEFAULT_SESSION_FACTORY = get_default_session_factory()
