from pathlib import Path

from openvair import config

RESTIC_DIR: Path = Path(config.data.get('backup', {}).get('restic_dir'))
RESTIC_PASSWORD: str = config.data.get('backup', {}).get('restic_pass')
