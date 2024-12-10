"""Module for managing backup-related operations in the service layer.

The module includes an interface definition for the backup service layer
manager, which outlines the methods that should be implemented by any class
responsible for managing backup operations.
"""

from typing import Protocol


class BackupServiceLayerManagerProtocolInterface(Protocol):
    """Interface for the BackupServiceLayerManager.

    This interface defines the methods that should be implemented by any class
    that manages backup-related operations in the service layer.
    """
    ...
