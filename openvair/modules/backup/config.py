from pathlib import Path

from openvair import config

API_SERVICE_LAYER_QUEUE_NAME: str = config.RPC_QUEUES.Backup.SERVICE_LAYER
SERVICE_LAYER_DOMAIN_QUEUE_NAME: str = config.RPC_QUEUES.Backup.DOMAIN_LAYER

RESTIC_DIR: Path = Path(config.data.get('backup', {}).get('repository'))
RESTIC_PASSWORD: str = config.data.get('backup', {}).get('password')
