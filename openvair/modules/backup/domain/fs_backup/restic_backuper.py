"""Implementation of file-system backups using Restic.

Defines the `ResticBackuper` class, which implements file-system backup
operations using the Restic tool.

Classes:
    ResticBackuper: Implements file-system backup and restore logic using
        Restic.
"""

from typing import Dict, List, Union
from pathlib import Path

from openvair.libs.log import get_logger
from openvair.modules.backup.domain.base import FSBackuper
from openvair.modules.backup.domain.schemas import (
    ResticSnapshot,
    ResticBackupResult,
    ResticRestoreResult,
)
from openvair.modules.backup.adapters.restic.restic import ResticAdapter
from openvair.modules.backup.adapters.restic.exceptions import ResticError

LOG = get_logger(__name__)


class ResticBackuper(FSBackuper):
    """File-system backuper using Restic.

    Implements backup, restore, repository initialization, and snapshot
    retrieval logic using the Restic tool.

    Attributes:
        source_path (Path): Path to the source directory or file to be backed
            up.
        restic_path (Path): Path to the Restic repository.
        restic (ResticAdapter): Adapter for interacting with Restic.
    """
    def __init__(
        self,
        source_path: str,
        restic_path: str,
        restic_password: str,
    ) -> None:
        """Initialize a ResticBackuper instance.

        Args:
            source_path (str): Path to the source directory or file to be backed
                up.
            restic_path (str): Path to the Restic repository.
            restic_password (str): Password for the Restic repository.
        """
        super().__init__(source_path)
        self.restic_path = restic_path
        self.restic = ResticAdapter(Path(restic_path), restic_password)

    def backup(self) -> Dict[str, Union[str, int]]:
        """Performs a backup of the specified source path.

        Returns:
            Dict[str, Union[str, int]]: Information about the backup process.
        """
        try:
            LOG.info(f'Backuping data from `{self.source_path}`...')
            bkp_data = self.restic.backup(self.source_path)
            LOG.info(f'Backup `{self.source_path}` cimplete')
            return ResticBackupResult.model_validate(bkp_data).model_dump()
        except ResticError as err:
            LOG.error(f'Error while backuping: {err!s}')
            raise

    def restore(self, data: Dict[str, str]) -> Dict[str, Union[str, int]]:
        """Restores data from a specific snapshot.

        Args:
            data (Dict[str, str]): Contains snapshot information, such as ID.

        Returns:
            Dict[str, Union[str, int]]: Information about the restore process.
        """
        snapshot_id = data.get('snapshot_id', 'latest')
        try:
            LOG.info(f'Restoring data from snapshot: `{snapshot_id}`...')
            restore_data = self.restic.restore(self.source_path, snapshot_id)
            LOG.info(f'Restoring data from snapshot `{snapshot_id}` complete')
            return ResticRestoreResult.model_validate(restore_data).model_dump()
        except ResticError as err:
            LOG.error(f'Error while restoring snapshot {snapshot_id}: {err!s}')
            raise

    def init_repository(self) -> None:
        """Initializes a new Restic repository."""
        try:
            LOG.info(f'Initializing repository `{self.restic_path}`...')
            self.restic.init_repository()
            LOG.info(f'Repository successful `{self.restic_path}` initilized')
        except ResticError as err:
            LOG.error(f'Error while creating repository: {err!s}')
            raise

    def get_snapshots(self) -> List[Dict]:
        """Retrieves a list of snapshots from the repository.

        Returns:
            List[Dict]: List of snapshot metadata.
        """
        try:
            LOG.info('Start getting snapshots...')
            snapshots = self.restic.snapshots()
            LOG.info('Getting snapshots success complete')
            return [
                ResticSnapshot.model_validate(snapshot).model_dump()
                for snapshot in snapshots
            ]
        except ResticError as err:
            LOG.error(f'Error while getting snapshots: {err!s}')
            raise
