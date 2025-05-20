"""CRUD operations for volume management.

This module defines a class for handling CRUD operations related to volumes.
The operations include retrieving, creating, updating, and deleting volumes
through communication with the service layer via RPC.

Classes:
    VolumeCrud: Class providing CRUD operations for volumes.
"""

from uuid import UUID
from typing import Dict, List, Optional

from openvair.libs.log import get_logger
from openvair.modules.volume.config import API_SERVICE_LAYER_QUEUE_NAME
from openvair.modules.volume.service_layer import services
from openvair.libs.messaging.messaging_agents import MessagingClient
from openvair.modules.volume.entrypoints.schemas import (
    Volume,
    CreateVolumeFromTemplate,
)
from openvair.modules.volume.adapters.dto.internal.commands import (
    CreateVolumeFromTemplateServiceCommandDTO,
)

LOG = get_logger(__name__)


class VolumeCrud:
    """Class providing CRUD operations for volumes.

    This class handles interactions with the service layer to perform CRUD
    operations on volume resources. It uses RPC to communicate with the
    service layer, ensuring that all volume-related operations are processed
    asynchronously.
    """

    def __init__(self) -> None:
        """Initialize the VolumeCrud class and set up the RPC client."""
        self.service_layer_rpc = MessagingClient(
            queue_name=API_SERVICE_LAYER_QUEUE_NAME
        )

    def get_volume(self, volume_id: UUID) -> Dict:
        """Retrieve a specific volume by its ID.

        Args:
            volume_id (str): The ID of the volume to retrieve.

        Returns:
            Dict: The retrieved volume's data as a dictionary.
        """
        LOG.info('Call service layer on getting volume.')
        result: Dict = self.service_layer_rpc.call(
            services.VolumeServiceLayerManager.get_volume.__name__,
            data_for_method={'volume_id': str(volume_id)},
            priority=8,
        )
        LOG.debug('Response from service layer: %s.' % result)
        return result

    def get_all_volumes(
        self,
        storage_id: Optional[UUID],
        *,
        free_volumes: bool = False,
    ) -> List:
        """Retrieve all volumes.

        Optionally filtering by storage or attachment status.

        Args:
            storage_id (Optional[str]): The ID of the storage to filter volumes
            by.
            free_volumes (Optional[bool]): If True, return only volumes without
                attachments.

        Returns:
            Page: A paginated list of volumes.
        """
        LOG.info('Call service layer on getting all volumes.')
        result: List = self.service_layer_rpc.call(
            services.VolumeServiceLayerManager.get_all_volumes.__name__,
            data_for_method={
                'storage_id': str(storage_id) if storage_id else None,
                'free_volumes': free_volumes,
            },
            priority=8,
        )
        LOG.debug('Response from service layer: %s.' % result)
        return result

    def create_volume(self, data: Dict, user_info: Dict) -> Dict:
        """Create a new volume.

        Args:
            data (Dict): The data required to create the volume.
            user_info (Dict): Information about the authenticated user.

        Returns:
            Dict: The created volume's data as a dictionary.
        """
        LOG.info('Call service layer on create volume.')
        data.update({'user_info': user_info})
        result: Dict = self.service_layer_rpc.call(
            services.VolumeServiceLayerManager.create_volume.__name__,
            data_for_method=data,
            priority=8,
        )
        LOG.debug('Response from service layer: %s.' % result)
        return result

    def delete_volume(self, volume_id: UUID, user_info: Dict) -> Dict:
        """Delete a specific volume by its ID.

        Args:
            volume_id (str): The ID of the volume to delete.
            user_info (Dict): Information about the authenticated user.

        Returns:
            Dict: The deleted volume's data as a dictionary.
        """
        LOG.info('Call service layer on delete volume.')
        result: Dict = self.service_layer_rpc.call(
            services.VolumeServiceLayerManager.delete_volume.__name__,
            data_for_method={
                'volume_id': str(volume_id),
                'user_info': user_info,
            },
            priority=8,
        )
        LOG.debug('Response from service layer: %s.' % result)
        return result

    def extend_volume(
        self,
        volume_id: UUID,
        data: Dict,
        user_info: Dict,
    ) -> Dict:
        """Extend an existing volume to a new size.

        Args:
            volume_id (str): The ID of the volume to extend.
            data (Dict): The new size data for the volume.
            user_info (Dict): Information about the authenticated user.

        Returns:
            Dict: The extended volume's data as a dictionary.
        """
        data.update({'volume_id': str(volume_id), 'user_info': user_info})
        LOG.info('Call service layer on extend volume.')
        result: Dict = self.service_layer_rpc.call(
            services.VolumeServiceLayerManager.extend_volume.__name__,
            data_for_method=data,
            priority=8,
        )
        LOG.debug('Response from service layer: %s.' % result)
        return result

    def edit_volume(self, volume_id: UUID, data: Dict, user_info: Dict) -> Dict:
        """Edit an existing volume's metadata.

        Args:
            volume_id (str): The ID of the volume to edit.
            data (Dict): The new metadata for the volume.
            user_info (Dict): Information about the authenticated user.

        Returns:
            Dict: The updated volume's data as a dictionary.
        """
        data.update(
            {
                'volume_id': str(volume_id),
                'user_info': user_info,
            }
        )
        LOG.info('Call service layer on edit volume.')
        result: Dict = self.service_layer_rpc.call(
            services.VolumeServiceLayerManager.edit_volume.__name__,
            data_for_method=data,
            priority=8,
        )
        LOG.debug('Response from service layer: %s.' % result)
        return result

    def attach_volume(
        self,
        volume_id: UUID,
        data: Dict,
        user_info: Dict,
    ) -> Dict:
        """Attach a volume to a virtual machine.

        Args:
            volume_id (str): The ID of the volume to attach.
            data (Dict): Information about the attachment.
            user_info (Dict): Information about the authenticated user.

        Returns:
            Dict: The attached volume's data as a dictionary.
        """
        data.update({'volume_id': str(volume_id), 'user_info': user_info})
        LOG.info('Call service layer on attach volume.')
        result: Dict = self.service_layer_rpc.call(
            services.VolumeServiceLayerManager.attach_volume.__name__,
            data_for_method=data,
            priority=8,
        )
        LOG.debug('Response from service layer: %s.' % result)
        return result

    def detach_volume(
        self,
        volume_id: UUID,
        detach_info: Dict,
        user_info: Dict,
    ) -> Dict:
        """Detach a volume from a virtual machine.

        Args:
            volume_id (str): The ID of the volume to detach.
            detach_info (Dict): Information about the detachment.
            user_info (Dict): Information about the authenticated user.

        Returns:
            Dict: The detached volume's data as a dictionary.
        """
        LOG.info('Call service layer on detach volume.')
        detach_info.update(
            {'volume_id': str(volume_id), 'user_info': user_info}
        )
        result: Dict = self.service_layer_rpc.call(
            services.VolumeServiceLayerManager.detach_volume.__name__,
            data_for_method=detach_info,
            priority=8,
        )
        LOG.debug('Response from service layer: %s.' % result)
        return result

    def create_from_template(  # noqa: D102
        self,
        data: CreateVolumeFromTemplate,
        user_info: Dict,
    ) -> Volume:
        command = CreateVolumeFromTemplateServiceCommandDTO(
            user_id=user_info['id'],
            **data.model_dump(),
        )
        volume = self.service_layer_rpc.call(
            services.VolumeServiceLayerManager.create_from_template.__name__,
            data_for_method=command.model_dump(mode='json')
        )
        return Volume.model_validate(volume)
