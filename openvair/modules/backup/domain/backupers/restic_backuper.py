"""Implementation of file-system backups using Restic.

This module defines the `ResticBackuper` class, which provides functionality
to perform file-system backups, restores, snapshot retrieval, and repository
initialization using the Restic tool. It includes error handling specific
to Restic operations.
"""

from typing import Dict, List, Union
from pathlib import Path

from openvair.libs.log import get_logger
from openvair.modules.backup.schemas import (
    ResticSnapshot,
    ResticBackupResult,
    ResticRestoreResult,
)
from openvair.modules.backup.domain.base import FSBackuper
from openvair.modules.backup.domain.exceptions import (
    BackupResticBackuperError,
    RestoreResticBackuperError,
    InitRepositoryResticBackuperError,
    SnapshotGettingResticBackuperError,
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

        Sets up paths and initializes a ResticAdapter instance for interacting
        with the Restic repository.

        Args:
            source_path (str): Path to the source directory or file to be backed
                up.
            restic_path (str): Path to the Restic repository directory.
            restic_password (str): Password for authenticating with the Restic
                repository.
        """
        super().__init__(source_path)
        self.restic_path = restic_path
        self.restic = ResticAdapter(Path(restic_path), restic_password)

    def backup(self) -> Dict[str, Union[str, int, None]]:
        """Performs a backup of the specified source path.

        This method uses the ResticAdapter to back up files or directories to
        the Restic repository. The output is validated and returned as a
        dictionary.

        Returns:
            Dict[str, Union[str, int]]: Information about the backup result,
                corresponding to the `ResticBackupResult` model from
                `openvair.modules.backup.domain.schemas`.

        Raises:
            BackupResticBackuperError: If the backup operation fails.
        """
        try:
            LOG.info(f'Backuping data from `{self.source_path}`...')
            bkp_data = self.restic.backup(self.source_path)
            LOG.info(f'Backup `{self.source_path}` cimplete')
            return ResticBackupResult.model_validate(bkp_data).model_dump()
        except ResticError as err:
            message = f'Error while backuping: {err!s}'
            LOG.error(message)
            raise BackupResticBackuperError(message)

    def restore(self, data: Dict[str, str]) -> Dict[str, Union[str, int, None]]:
        """Restores data from a specific snapshot.

        This method restores files or directories from a snapshot stored in the
        Restic repository. The snapshot ID is provided in the `data` argument.

        Args:
            data (Dict[str, str]): Dictionary containing snapshot information.
                Must include the key `snapshot_id`.

        Returns:
            Dict[str, Union[str, int]]: Information about the restore result,
                corresponding to the `ResticRestoreResult` model from
                `openvair.modules.backup.domain.schemas`.

        Raises:
            RestoreResticBackuperError: If the restore operation fails.
        """
        snapshot_id = data.get('snapshot_id', 'latest')
        try:
            LOG.info(f'Restoring data from snapshot: `{snapshot_id}`...')
            restore_data = self.restic.restore(self.source_path, snapshot_id)
            LOG.info(f'Restoring data from snapshot `{snapshot_id}` complete')
            return ResticRestoreResult.model_validate(restore_data).model_dump()
        except ResticError as err:
            message = f'Error while restoring snapshot {snapshot_id}: {err!s}'
            LOG.error(message)
            raise RestoreResticBackuperError(message)

    def init_repository(self) -> None:
        """Initializes a new Restic repository.

        This method uses the ResticAdapter to create a new repository for
        storing backups. It ensures that the repository is properly
        initialized.

        Raises:
            InitRepositoryResticBackuperError: If the repository initialization
                fails.
        """
        try:
            LOG.info(f'Initializing repository `{self.restic_path}`...')
            self.restic.init_repository()
            LOG.info(f'Repository successful `{self.restic_path}` initilized')
        except ResticError as err:
            message = f'Error while creating repository: {err!s}'
            LOG.error(message)
            raise InitRepositoryResticBackuperError(message)

    def get_snapshots(self) -> List[Dict]:
        """Restores data from a specific snapshot.

        This method restores files or directories from a snapshot stored in the
        Restic repository. The snapshot ID is provided in the `data` argument.

        Args:
            data (Dict[str, str]): Dictionary containing snapshot information.
                Must include the key `snapshot_id`.

        Returns:
            Dict[str, Union[str, int]]: Information about the restore process,
                corresponding to the `ResticRestoreResult` model from
                `openvair.modules.backup.domain.schemas`.

        Raises:
            RestoreResticBackuperError: If the restore operation fails.
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
            message = f'Error while getting snapshots: {err!s}'
            LOG.error(message)
            raise SnapshotGettingResticBackuperError(message)
