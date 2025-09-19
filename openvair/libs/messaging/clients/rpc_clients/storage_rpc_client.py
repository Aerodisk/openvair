"""Proxy implementation for the Storage Service Layer.

This module defines the `StorageServiceLayerClient` class, which serves as a
proxy for interacting with the Storage Service Layer. The proxy class
encapsulates the details of the RPC communication with the service layer,
providing a consistent and easy-to-use interface for external code.

The `StorageServiceLayerClient` class implements the
`StorageServiceLayerProtocolInterface`, which defines the contract for
interacting with the storage service layer. This allows the external code
to work with the proxy class without needing to know the underlying
implementation details.

Classes:
    StorageServiceLayerClient: Proxy implementation for the Storage Service
        Layer, providing a consistent interface for interacting with the
        storage service.
"""


from openvair.rpc_queues import RPCQueueNames
from openvair.libs.messaging.messaging_agents import MessagingClient
from openvair.libs.messaging.service_interfaces.storage import (
    StorageServiceLayerProtocolInterface,
)


class StorageServiceLayerRPCClient(StorageServiceLayerProtocolInterface):
    """Proxy implementation for StorageServiceLayerProtocolInterface

    This class provides methods to interact with the Storage Service Layer
    through RPC calls.

    Attributes:
        storage_service_rpc (RabbitRPCClient): RPC client for communicating with
            the Storage Service Layer.
    """

    def __init__(self) -> None:
        """Initialize the StorageServiceLayerClient.

        This method sets up the necessary components for the
        StorageServiceLayerClient, including the RabbitMQ RPC client for
        communicating with the Storage Service Layer.
        """
        self.service_rpc_client = MessagingClient(
            queue_name=RPCQueueNames.Storage.SERVICE_LAYER
        )

    def get_storage(self, data: dict) -> dict:
        """Retrieve a storage by its ID.

        Args:
            data (Dict): Data containing the storage ID.

        Returns:
            Dict: Serialized storage data.
        """
        result: dict = self.service_rpc_client.call(
            StorageServiceLayerProtocolInterface.get_storage.__name__,
            data_for_method=data,
        )
        return result

    def get_all_storages(self) -> list[dict]:
        """Retrieve all storages from the database.

        Returns:
            List[Dict]: List of serialized storage data.
        """
        result: list[dict] = self.service_rpc_client.call(
            StorageServiceLayerProtocolInterface.get_all_storages.__name__,
            data_for_method={},
        )
        return result

    def create_local_partition(self, data: dict) -> dict:
        """Create a local partition on the disk.

        Args:
            data (Dict): Data containing details for creating the partition.

        Returns:
            Dict: Serialized partition data.
        """
        result: dict = self.service_rpc_client.call(
            StorageServiceLayerProtocolInterface.create_local_partition.__name__,
            data_for_method=data,
        )
        return result

    def get_local_disk_partitions_info(self, data: dict) -> dict:
        """Get information about local disk partitions.

        Args:
            data (Dict): Data containing the disk path.

        Returns:
            Dict: Partition information.
        """
        result: dict = self.service_rpc_client.call(
            StorageServiceLayerProtocolInterface.get_local_disk_partitions_info.__name__,
            data_for_method=data,
        )
        return result

    def delete_local_partition(self, data: dict) -> dict:
        """Delete a local partition.

        Args:
            data (Dict): Data containing details for deleting the partition.

        Returns:
            Dict: Result of the delete operation.
        """
        result: dict = self.service_rpc_client.call(
            StorageServiceLayerProtocolInterface.delete_local_partition.__name__,
            data_for_method=data,
        )
        return result

    def create_storage(self, data: dict) -> dict:
        """Create a new storage.

        Args:
            data (Dict): Data containing details for creating the storage.

        Returns:
            Dict: Serialized storage data.
        """
        result: dict = self.service_rpc_client.call(
            StorageServiceLayerProtocolInterface.create_storage.__name__,
            data_for_method=data,
        )
        return result

    def delete_storage(self, data: dict) -> dict:
        """Delete a storage.

        Args:
            data (Dict): Data containing the storage ID.

        Returns:
            Dict: Serialized storage data.
        """
        result: dict = self.service_rpc_client.call(
            StorageServiceLayerProtocolInterface.delete_storage.__name__,
            data_for_method=data,
        )
        return result

    def get_local_disks(self, data: dict) -> list:
        """Retrieve local disks information.

        Args:
            data (Dict): Data containing details for filtering disks.

        Returns:
            List: List of local disks.
        """
        result: list = self.service_rpc_client.call(
            StorageServiceLayerProtocolInterface.get_local_disks.__name__,
            data_for_method=data,
        )
        return result
