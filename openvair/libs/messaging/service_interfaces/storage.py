"""Module for managing the Storage Service Layer.

This module defines the `StorageServiceLayerManagerInterface`, which serves as
the contract for handling storage-related operations in the service layer.
Any class implementing this interface is responsible for interacting with the
domain layer and the event store to perform various tasks, such as retrieving
storage information, creating and deleting.

Classes:
    StorageServiceLayerManagerInterface: Interface for handling storage service
        layer operations.
"""

from typing import Dict, List, Protocol


class StorageServiceLayerProtocolInterface(Protocol):
    """Interface for the StorageServiceLayerManager.

    This interface defines the methods that should be implemented by any class
    that manages storage-related operations in the service layer.
    """

    def get_storage(self, data: Dict) -> Dict:
        """Retrieve a storage by its ID.

        Args:
            data (Dict): Data containing the storage ID.

        Returns:
            Dict: Serialized storage data.
        """
        ...

    def get_all_storages(self) -> List[Dict]:
        """Retrieve all storages from the database.

        Returns:
            List[Dict]: List of serialized storage data.
        """
        ...

    def create_local_partition(self, data: Dict) -> Dict:
        """Create a local partition on the disk.

        Args:
            data (Dict): Data containing details for creating the partition.

        Returns:
            Dict: Serialized partition data.
        """
        ...

    def get_local_disk_partitions_info(self, data: Dict) -> Dict:
        """Get information about local disk partitions.

        Args:
            data (Dict): Data containing the disk path.

        Returns:
            Dict: Partition information.
        """
        ...

    def delete_local_partition(self, data: Dict) -> Dict:
        """Delete a local partition.

        Args:
            data (Dict): Data containing details for deleting the partition.

        Returns:
            Dict: Result of the delete operation.
        """
        ...

    def create_storage(self, data: Dict) -> Dict:
        """Create a new storage.

        Args:
            data (Dict): Data containing details for creating the storage.

        Returns:
            Dict: Serialized storage data.
        """
        ...

    def delete_storage(self, data: Dict) -> Dict:
        """Delete a storage.

        Args:
            data (Dict): Data containing the storage ID.

        Returns:
            Dict: Serialized storage data.
        """
        ...

    def get_local_disks(self, data: Dict) -> List:
        """Retrieve local disks information.

        Args:
            data (Dict): Data containing details for filtering disks.

        Returns:
            List: List of local disks.
        """
        ...
