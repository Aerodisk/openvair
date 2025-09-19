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

from typing import Protocol


class TemplateServiceLayerProtocolInterface(Protocol):
    """Interface for the StorageServiceLayerManager.

    This interface defines the methods that should be implemented by any class
    that manages storage-related operations in the service layer.
    """

    def get_all_templates(self) -> list: ...  # noqa: D102

    def get_template(self, getting_data: dict) -> dict: ...  # noqa: D102

    def create_template(self, creating_data: dict) -> dict: ...  # noqa: D102

    def edit_template(self, updating_data: dict) -> dict: ...  # noqa: D102

    def delete_template(self, deleting_data: dict) -> dict: ...  # noqa: D102
