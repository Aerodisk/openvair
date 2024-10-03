import tempfile

from openvair.config import RPC_QUEUES, get_default_session_factory

API_SERVICE_LAYER_QUEUE_NAME: str = RPC_QUEUES.Image.SERVICE_LAYER
SERVICE_LAYER_DOMAIN_QUEUE_NAME: str = RPC_QUEUES.Image.DOMAIN_LAYER

TMP_DIR = tempfile.gettempdir()
CHUNK_SIZE = 1024 * 1024
PERMITTED_EXTENSIONS = ['iso']

DEFAULT_SESSION_FACTORY = get_default_session_factory()
