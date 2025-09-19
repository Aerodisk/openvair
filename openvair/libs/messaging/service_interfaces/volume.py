"""Module for managing the Volume Service Layer.

This module defines the `VolumeServiceLayerManagerInterface`, which serves as
the contract for handling volume-related operations in the service layer.
Any class implementing this interface is responsible for interacting with the
domain layer and the event store to perform various tasks, such as retrieving
volume information, creating, extending, deleting, and attaching volumes.

Classes:
    VolumeServiceLayerManagerInterface: Interface for handling volume service
        layer operations.
"""

from typing import Protocol


class VolumeServiceLayerProtocolInterface(Protocol):
    """Interface for the VolumeServiceLayerManager.

    This interface defines the methods that should be implemented by any class
    that manages volume-related operations in the service layer.
    """

    def get_volume(self, data: dict) -> dict:
        """Retrieve a volume by its ID.

        Args:
            data (Dict): Data containing the volume ID.

        Returns:
            Dict: Serialized volume data.
        """
        ...

    def get_all_volumes(self, data: dict) -> list[dict]:
        """Retrieve all volumes from the database.

        Args:
            data (Dict): Data for filtering volumes.

        Returns:
            List[Dict]: List of serialized volume data.
        """
        ...

    def create_volume(self, volume_info: dict) -> dict:
        """Create a new volume.

        Args:
            volume_info (Dict): Information about the volume to be created.

        Returns:
            Dict: Serialized volume data.
        """
        ...

    def clone_volume(self, data: dict) -> dict:
        """Clone an existing volume.

        Args:
            data (Dict): Data containing the source volume information.

        Returns:
            Dict: Serialized cloned volume data.
        """
        ...

    def create_from_template(self, data: dict) -> dict:
        """Create a new volume from a template.

        Args:
            data (Dict): Data containing the template ID and volume details.

        Returns:
            Dict: Serialized volume data.
        """
        ...

    def extend_volume(self, data: dict) -> dict:
        """Extend the size of an existing volume.

        Args:
            data (Dict): Data containing the volume ID and new size.

        Returns:
            Dict: Serialized volume data.
        """
        ...

    def delete_volume(self, data: dict) -> dict:
        """Delete an existing volume.

        Args:
            data (Dict): Data containing the volume ID.

        Returns:
            Dict: Serialized volume data.
        """
        ...

    def edit_volume(self, data: dict) -> dict:
        """Edit the details of an existing volume.

        Args:
            data (Dict): Data containing the volume ID and new details.

        Returns:
            Dict: Serialized volume data.
        """
        ...

    def attach_volume(self, data: dict) -> dict:
        """Attach a volume to a virtual machine.

        Args:
            data (Dict): Data containing the volume ID and VM details.

        Returns:
            Dict: Result of the attach operation.
        """
        ...

    def detach_volume(self, data: dict) -> dict:
        """Detach a volume from a virtual machine.

        Args:
            data (Dict): Data containing the volume ID and VM details.

        Returns:
            Dict: Result of the detach operation.
        """
        ...
