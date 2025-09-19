"""CRUD operations for managing backups.

This module defines the `BackupCrud` class, which acts as a bridge between
API endpoints and the service layer. It uses the `MessagingClient` to
communicate with the service layer and provides methods for creating
backups, restoring data, retrieving snapshots, and initializing backup
repositories.

Classes:
    BackupCrud: Provides CRUD operations for managing backups.
"""


from openvair.modules.backup.config import API_SERVICE_LAYER_QUEUE_NAME
from openvair.modules.backup.schemas import (
    ResticSnapshot,
    ResticBackupResult,
    ResticDeleteResult,
    ResticRestoreResult,
)
from openvair.libs.messaging.messaging_agents import MessagingClient
from openvair.modules.backup.service_layer.services import (
    BackupServiceLayerManager,
)


class BackupCrud:
    """CRUD operations for backup management.

    This class interacts with the service layer via `MessagingClient`
    to perform backup operations such as creating backups, restoring data,
    fetching snapshots, and initializing repositories.

    Attributes:
        service_layer_rpc (MessagingClient): Client for interacting with
            the service layer RPC.
    """

    def __init__(self) -> None:
        """Initialize the BackupCrud instance.

        Sets up the messaging client for interacting with the service layer.

        Args:
            None
        """
        self.service_layer_rpc = MessagingClient(
            queue_name=API_SERVICE_LAYER_QUEUE_NAME
        )

    def create_backup(self) -> ResticBackupResult:
        """Create a new backup.

        This method calls the service layer to initiate a backup process.

        Returns:
            ResticBackupResult: The result of the backup operation.
        """
        backup_info = self.service_layer_rpc.call(
            BackupServiceLayerManager.create_backup.__name__,
        )
        return ResticBackupResult(**backup_info)

    def restore_backup(self, snapshot_id: str) -> ResticRestoreResult:
        """Restore data from a specific snapshot.

        This method calls the service layer to restore data from a given
        snapshot.

        Args:
            snapshot_id (str): ID of the snapshot to restore.

        Returns:
            ResticRestoreResult: The result of the restore operation.
        """
        backup_info = self.service_layer_rpc.call(
            BackupServiceLayerManager.restore_backup.__name__,
            data_for_method={'snapshot_id': snapshot_id},
        )
        return ResticRestoreResult(**backup_info)

    def get_snapshots(self) -> list[ResticSnapshot]:
        """Retrieve a list of available snapshots.

        This method calls the service layer to fetch metadata for all snapshots.

        Returns:
            List[ResticSnapshot]: A list of snapshot metadata.
        """
        snapshots = self.service_layer_rpc.call(
            BackupServiceLayerManager.get_snapshots.__name__
        )
        return [ResticSnapshot(**snapshot) for snapshot in snapshots]

    def initialize_backup_repository(self) -> None:
        """Initialize the backup repository.

        This method calls the service layer to create and configure the backup
        repository.

        Returns:
            None
        """
        self.service_layer_rpc.call(
            BackupServiceLayerManager.initialize_backup_repository.__name__
        )

    def delete_snapshot(self, snapshot_id: str) -> ResticDeleteResult:
        """Delete a specific backup snapshot.

        This method calls the service layer to remove a snapshot from the
        backup repository.

        Args:
            snapshot_id (str): ID of the snapshot to delete.

        Returns:
            ResticDeleteResult: The result of the deletion operation.
        """
        delete_info = self.service_layer_rpc.call(
            BackupServiceLayerManager.delete_snapshot.__name__,
            data_for_method={'snapshot_id': snapshot_id},
        )
        return ResticDeleteResult(**delete_info)
