from typing import Dict, List, Union, overload
from pathlib import Path

from openvair.modules.backup.domain.base import FSBackuper
from openvair.modules.backup.adapters.restic.restic import ResticAdapter


class ResticBackuper(FSBackuper):
    def __init__(
        self,
        source_path: str,
        restic_path: str,
        restic_password: str,
    ) -> None:
        super().__init__(source_path)
        self.restic = ResticAdapter(Path(restic_path), restic_password)

    def backup(self) -> Dict[str, Union[str, int]]:
        bkp_data = self.restic.backup(self.source_path)
        return {}

    def restore(self, data: Dict[str, str]) -> Dict[str, Union[str, int]]:
        bkp_id = data['bkp_id']
        restore_data = self.restic.restore(self.source_path, bkp_id)
        return {}

    def init_repository(self) -> Dict[str, str]:
        self.restic.init_repository()
        return {}

    def get_snapshots(self) -> List[Dict]:
        self.restic.snapshots()
        return []
