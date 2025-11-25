from openvair.config import RPC_QUEUES, get_default_session_factory

API_SERVICE_LAYER_QUEUE_NAME: str = RPC_QUEUES.VirtualNetwork.SERVICE_LAYER
SERVICE_LAYER_DOMAIN_QUEUE_NAME: str = RPC_QUEUES.VirtualNetwork.DOMAIN_LAYER

DEFAULT_SESSION_FACTORY = get_default_session_factory()
