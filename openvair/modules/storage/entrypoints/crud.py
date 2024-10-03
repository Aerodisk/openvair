"""CRUD operations for storage-related services.

This module provides the CRUD (Create, Read, Update, Delete) operations for
interacting with the service layer that manages storage and local disk
partitions.

Classes:
    StorageCrud: Class providing methods to perform CRUD operations on storages
        and partitions.
"""

from typing import Dict

from fastapi_pagination import Page, paginate

from openvair.libs.log import get_logger
from openvair.modules.tools.utils import validate_objects
from openvair.modules.storage.config import API_SERVICE_LAYER_QUEUE_NAME
from openvair.libs.messaging.protocol import Protocol
from openvair.modules.storage.entrypoints import schemas
from openvair.modules.storage.service_layer import services

LOG = get_logger(__name__)


class StorageCrud:
    """CRUD class for managing storage and partition operations.

    This class provides methods to create, read, and delete storage objects
    and manage local disk partitions by interacting with the service layer.
    """

    def __init__(self):
        """Initialize the StorageCrud with service layer RPC."""
        self.service_layer_rpc = Protocol(client=True)(
            API_SERVICE_LAYER_QUEUE_NAME
        )

    def get_storage(self, storage_id: str) -> Dict:
        """Retrieve a storage by its ID.

        Args:
            storage_id (str): The ID of the storage to retrieve.

        Returns:
            Dict: The storage object data retrieved from the service layer.
        """
        LOG.info('Call service layer on getting storage.')
        result = self.service_layer_rpc.call(
            services.StorageServiceLayerManager.get_storage.__name__,
            data_for_method={'storage_id': storage_id},
        )
        LOG.debug('Response from service layer: %s.' % result)
        return result

    def get_all_storages(self) -> Page:
        """Retrieve all storages from the database.

        Returns:
            Page: A paginated list of all storages.
        """
        LOG.info('Call service layer on getting all storages.')
        result = self.service_layer_rpc.call(
            services.StorageServiceLayerManager.get_all_storages.__name__,
            data_for_method={},
        )
        LOG.debug('Response from service layer: %s.' % result)
        storages = validate_objects(result, schemas.Storage)
        return paginate(storages)

    def create_storage(self, data: Dict, user_data: Dict) -> Dict:
        """Create a new storage.

        Args:
            data (Dict): The data required to create the storage.
            user_data (Dict): User information for the operation.

        Returns:
            Dict: The created storage object data.
        """
        LOG.info('Call service layer on create storage.')
        data.update({'user_data': user_data})
        result = self.service_layer_rpc.call(
            services.StorageServiceLayerManager.create_storage.__name__,
            data_for_method=data,
            priority=8,
        )
        LOG.debug('Response from service layer: %s.' % result)
        return result

    def delete_storage(self, storage_id: str, user_data: Dict) -> Dict:
        """Delete a storage by its ID.

        Args:
            storage_id (str): The ID of the storage to delete.
            user_data (Dict): User information for the operation.

        Returns:
            Dict: Confirmation of the deletion operation.
        """
        LOG.info('Call service layer on delete storage.')
        result = self.service_layer_rpc.call(
            services.StorageServiceLayerManager.delete_storage.__name__,
            data_for_method={'storage_id': storage_id, 'user_data': user_data},
            priority=8,
        )
        LOG.debug('Response from service layer: %s.' % result)
        return result

    def get_local_disks(
        self, data: Dict
    ) -> schemas.ListOfLocalDisks:
        """Retrieve a list of local disks.

        Args:
            data (Dict): dictionary containing information about the disks
                getting
                    - free_local_disks (bool): Whether to retrieve only free
                        local disks.

        Returns:
            schemas.ListOfLocalDisks: A list of local disks.
        """
        LOG.info('Call service layer on get free local disks.')
        result = self.service_layer_rpc.call(
            services.StorageServiceLayerManager.get_local_disks.__name__,
            data_for_method={
                'free_local_disks': data.get('free_local_disks', False)
            },
        )
        LOG.debug('Response from service layer: %s.' % result)
        local_disks = validate_objects(result, schemas.LocalDisk)
        return schemas.ListOfLocalDisks(disks=local_disks)

    def create_local_partition(self, data: Dict, user_data: Dict) -> Dict:
        """Create a new partition on a local disk.

        Args:
            data (Dict): The data required to create the partition.
            user_data (Dict): User information for the operation.

        Returns:
            Dict: Information about the created partition.
        """
        LOG.info('Call service layer on creating partition.')
        data['user_data'] = user_data
        result = self.service_layer_rpc.call(
            services.StorageServiceLayerManager.create_local_partition.__name__,
            data_for_method=data,
        )
        LOG.info('Response from service layer successfully completed.')
        return result

    def get_local_disk_partitions_info(self, data: Dict) -> Dict:
        """Get information about partitions on a local disk.

        Args:
            data (Dict): The data required to retrieve partition information.

        Returns:
            Dict: Information about the partitions on the specified disk.
        """
        LOG.info('Call service layer on getting local partitions.')
        result = self.service_layer_rpc.call(
            services.StorageServiceLayerManager.get_local_disk_partitions_info.__name__,
            data_for_method=data,
        )
        LOG.info('Response from service layer: %s.' % result)
        return result

    def delete_local_partition(self, data: Dict, user_data: Dict) -> Dict:
        """Delete a partition from a local disk.

        Args:
            data (Dict): The data required to delete the partition.
            user_data (Dict): User information for the operation.

        Returns:
            Dict: Confirmation of the deletion operation.
        """
        LOG.info('Call service layer on deleting partition.')
        data['user_data'] = user_data
        result = self.service_layer_rpc.call(
            services.StorageServiceLayerManager.delete_local_partition.__name__,
            data_for_method=data,
        )
        LOG.info('Response from service layer successfully completed.')
        return result

    def edit_local_partition(self, data: Dict) -> Dict:
        """Edit an existing partition on a local disk.

        Args:
            data (Dict): The data required to edit the partition.

        Returns:
            Dict: Information about the edited partition.
        """
        LOG.info('Call service layer on editing partition.')
        result = self.service_layer_rpc.call(
            services.StorageServiceLayerManager.edit_local_partition.__name__,
            data_for_method=data,
        )
        LOG.info('Response from service layer successfully completed.')
        return result
