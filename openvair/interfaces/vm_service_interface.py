"""Module for managing the Virtual Machine (VM) Service Layer.

This module defines the `VMServiceLayerProtocolInterface`, which serves as
the contract for handling VM-related operations in the service layer.
Any class implementing this interface is responsible for interacting with the
domain layer and the event store to perform various tasks, such as retrieving
VM information, creating, editing, deleting, starting, and stopping VMs.

Classes:
    VMServiceLayerProtocolInterface: Interface for handling VM service
        layer operations.
"""
from typing import Dict, List, Protocol


class VMServiceLayerProtocolInterface(Protocol):
    """Interface for the VMServiceLayerManager.

    This interface defines the methods that should be implemented by any class
    that manages VM-related operations in the service layer.
    """

    def get_vm(self, data: Dict) -> Dict:
        """Retrieve a VM by its ID.

        Args:
            data (Dict): Data containing the VM ID.

        Returns:
            Dict: Serialized VM data.
        """
        ...

    def get_all_vms(self) -> List[Dict]:
        """Retrieve all VMs from the database.

        Returns:
            List[Dict]: List of serialized VM data.
        """
        ...

    def create_vm(self, data: Dict) -> Dict:
        """Create a new VM.

        Args:
            data (Dict): Information about the VM to be created.

        Returns:
            Dict: Serialized VM data.
        """
        ...

    def delete_vm(self, data: Dict) -> Dict:
        """Delete an existing VM.

        Args:
            data (Dict): Data containing the VM ID.

        Returns:
            Dict: Serialized VM data.
        """
        ...

    def start_vm(self, data: Dict) -> Dict:
        """Start a VM.

        Args:
            data (Dict): Data containing the VM ID.

        Returns:
            Dict: Serialized VM data.
        """
        ...

    def shut_off_vm(self, data: Dict) -> Dict:
        """Shut off a VM.

        Args:
            data (Dict): Data containing the VM ID.

        Returns:
            Dict: Serialized VM data.
        """
        ...

    def edit_vm(self, edit_info: Dict) -> Dict:
        """Edit an existing VM.

        Args:
            edit_info (Dict): Information about the VM to be edited.

        Returns:
            Dict: Serialized VM data.
        """
        ...

    def vnc(self, data: Dict) -> Dict:
        """Retrieve VNC information for a VM.

        Args:
            data (Dict): Data containing the VM ID.

        Returns:
            Dict: VNC connection data.
        """
        ...

