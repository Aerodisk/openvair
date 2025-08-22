from openvair import config
from openvair.config import RPC_QUEUES, get_default_session_factory

API_SERVICE_LAYER_QUEUE_NAME: str = RPC_QUEUES.VMS.SERVICE_LAYER
SERVICE_LAYER_DOMAIN_QUEUE_NAME: str = RPC_QUEUES.VMS.DOMAIN_LAYER
VM_DRIVER = 'qemu-driver'
TEMPLATES_PATH = (
    '/opt/aero/openvair/openvair/modules/virtual_machines/domain/templates/'
)
SNAPSHOTS_PATH = (
    '/opt/aero/openvair/data/snapshots/'
)
SERVER_IP = config.data.get('web_app', {}).get('host', 'localhost')

# VNC WebSocket port configuration
VNC_WS_PORT_START = 6100
VNC_WS_PORT_END = 6999  # 900 ports available
VNC_LOCK_FILE = '/var/lock/openvair_vnc_ports.lock'
VNC_STATE_FILE = '/opt/aero/openvair/data/vnc_ports.json'
VNC_MAX_SESSIONS = 800  # Leave some buffer

DEFAULT_SESSION_FACTORY = get_default_session_factory()
