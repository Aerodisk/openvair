from pathlib import Path

from openvair import config

API_SERVICE_LAYER_QUEUE_NAME: str = config.RPC_QUEUES.Backup.SERVICE_LAYER
SERVICE_LAYER_DOMAIN_QUEUE_NAME: str = config.RPC_QUEUES.Backup.DOMAIN_LAYER


BACKUPER_TYPE = config.data.get('backup', {}).get('backuper')

RESTIC_DIR: Path = Path(
    config.data.get('backup', {}).get('restic').get('repository')
)
RESTIC_PASSWORD: str = (
    config.data.get('backup', {}).get('restic').get('password')
)

DEFAULT_SESSION_FACTORY = config.get_default_session_factory()
STORAGE_DATA = Path(config.data['storage'].get('data_path', ''))
