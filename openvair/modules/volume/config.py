from openvair.config import RPC_QUEUES, get_default_session_factory

API_SERVICE_LAYER_QUEUE_NAME: str  = RPC_QUEUES.Volume.SERVICE_LAYER
SERVICE_LAYER_DOMAIN_QUEUE_NAME: str  = RPC_QUEUES.Volume.DOMAIN_LAYER
DEFAULT_VOLUME_FORMAT = 'qcow2'

DEFAULT_SESSION_FACTORY = get_default_session_factory()
