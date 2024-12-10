"""Service layer for managing backups."""

from openvair.modules.base_manager import BackgroundTasks


class BackupServiceLayerManager(BackgroundTasks):
    """Manager for backup operations in the service layer.

    This class manages backup operations by coordinating communication
    between the service layer, domain layer, and the restic adapter.

    Attributes:
        ...
    """
    ...
