"""Repository pattern for volume-related database operations.

This module defines the repository pattern for managing volume-related data.
It abstracts the database operations for volumes, making it easier to interact
with the database while keeping the business logic separate.

Classes:
    AbstractRepository: Abstract base class for the volume repository.
    SqlAlchemyRepository: Concrete implementation of the repository using
        SQLAlchemy.
"""

import abc
from uuid import UUID
from typing import TYPE_CHECKING, Dict, List, Optional

from sqlalchemy import update
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import joinedload

from openvair.abstracts.exceptions import DBCannotBeConnectedError
from openvair.modules.volume.adapters.orm import Volume

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class AbstractRepository(metaclass=abc.ABCMeta):
    """Abstract base class for the volume repository.

    This class defines the interface for managing volumes in the database. It
    includes methods for adding, retrieving, deleting, and updating volumes.

    Methods:
        _check_connection: Check if the database connection is active.
        add: Add a new volume to the repository.
        get: Retrieve a volume by its ID.
        get_all: Retrieve all volumes.
        get_all_by_storage: Retrieve all volumes associated with a specific
            storage.
        get_by_name_and_storage: Retrieve a volume by its name and storage ID.
        delete: Delete a volume by its ID.
        bulk_update: Perform a bulk update on a list of volumes.
    """

    def _check_connection(self) -> None:
        """Check if the database connection is active.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError

    def add(self, volume: Volume) -> None:
        """Add a new volume to the repository.

        Args:
            volume (Volume): The volume object to add.
        """
        self._add(volume)

    def get(self, volume_id: UUID) -> Volume:
        """Retrieve a volume by its ID.

        Args:
            volume_id (UUID): The ID of the volume to retrieve.

        Returns:
            Volume: The retrieved volume object.
        """
        return self._get(volume_id)

    def get_all(self) -> List[Volume]:
        """Retrieve all volumes from the repository.

        Returns:
            List[Volume]: A list of all volumes.
        """
        return self._get_all()

    def get_all_by_storage(self, storage_id: str) -> List[Volume]:
        """Retrieve all volumes associated with a specific storage.

        Args:
            storage_id (str): The ID of the storage.

        Returns:
            List[Volume]: A list of volumes associated with the specified
                storage.
        """
        return self._get_all_by_storage(storage_id)

    def get_by_name_and_storage(
        self,
        volume_name: str,
        storage_id: str,
    ) -> Optional[Volume]:
        """Retrieve a volume by its name and storage ID.

        Args:
            volume_name (str): The name of the volume.
            storage_id (str): The ID of the storage.

        Returns:
            Volume: The retrieved volume object.
        """
        return self._get_by_name_and_storage(volume_name, storage_id)

    def delete(self, volume_id: UUID) -> None:
        """Delete a volume by its ID.

        Args:
            volume_id (UUID): The ID of the volume to delete.
        """
        self._delete(volume_id)

    def bulk_update(self, data: List[Dict]) -> None:
        """Perform a bulk update on a list of volumes.

        Args:
            data (List[Volume]): A list of volumes with updated data.
        """
        self._bulk_update(data)

    @abc.abstractmethod
    def _add(self, volume: Volume) -> None:
        """Add a new volume to the repository.

        Args:
            volume (Volume): The volume object to add.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _get(self, volume_id: UUID) -> Volume:
        """Retrieve a volume by its ID.

        Args:
            volume_id (UUID): The ID of the volume to retrieve.

        Returns:
            Volume: The retrieved volume object.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _get_all(self) -> List[Volume]:
        """Retrieve all volumes from the repository.

        Returns:
            List[Volume]: A list of all volumes.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _get_all_by_storage(self, storage_id: str) -> List[Volume]:
        """Retrieve all volumes associated with a specific storage.

        Args:
            storage_id (str): The ID of the storage.

        Returns:
            List[Volume]: A list of volumes associated with the specified
                storage.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _get_by_name_and_storage(
        self,
        volume_name: str,
        storage_id: str,
    ) -> Optional[Volume]:
        """Retrieve a volume by its name and storage ID.

        Args:
            volume_name (str): The name of the volume.
            storage_id (str): The ID of the storage.

        Returns:
            Volume: The retrieved volume object.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _delete(self, volume_id: UUID) -> None:
        """Delete a volume by its ID.

        Args:
            volume_id (UUID): The ID of the volume to delete.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _bulk_update(self, data: List[Dict]) -> None:
        """Perform a bulk update on a list of volumes.

        Args:
            data (List[Volume]): A list of volumes with updated data.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    """SQLAlchemy implementation of the volume repository.

    This class provides concrete implementations of the repository methods
    using SQLAlchemy to interact with the database.

    Attributes:
        session (Session): The SQLAlchemy session used for database operations.
    """

    def __init__(self, session: 'Session'):
        """Initialize the repository with a SQLAlchemy session.

        Args:
            session (Session): The SQLAlchemy session used for database
                operations.
        """
        super().__init__()
        self.session: Session = session
        self._check_connection()

    def _check_connection(self) -> None:
        """Check if the database connection is active.

        Raises:
            DBCannotBeConnectedError: If the database cannot be connected.
        """
        try:
            self.session.connection()
        except OperationalError:
            raise DBCannotBeConnectedError(message="Can't connect to Database")

    def _get(self, volume_id: UUID) -> Volume:
        """Retrieve a volume by its ID.

        Args:
            volume_id (UUID): The ID of the volume to retrieve.

        Returns:
            Volume: The retrieved volume object.
        """
        return (
            self.session.query(Volume)
            .options(joinedload(Volume.attachments))
            .filter_by(id=volume_id)
            .one()
        )

    def _add(self, volume: Volume) -> None:
        """Add a new volume to the repository.

        Args:
            volume (Volume): The volume object to add.
        """
        self.session.add(volume)

    def _get_all(self) -> List[Volume]:
        """Retrieve all volumes from the repository.

        Returns:
            List[Volume]: A list of all volumes.
        """
        return (
            self.session.query(Volume)
            .options(joinedload(Volume.attachments))
            .all()
        )

    def _get_all_by_storage(self, storage_id: str) -> List[Volume]:
        """Retrieve all volumes associated with a specific storage.

        Args:
            storage_id (str): The ID of the storage.

        Returns:
            List[Volume]: A list of volumes associated with the specified
                storage.
        """
        return (
            self.session.query(Volume)
            .options(joinedload(Volume.attachments))
            .filter_by(storage_id=storage_id)
            .all()
        )

    def _get_by_name_and_storage(
        self,
        volume_name: str,
        storage_id: str,
    ) -> Optional[Volume]:
        """Retrieve a volume by its name and storage ID.

        Args:
            volume_name (str): The name of the volume.
            storage_id (str): The ID of the storage.

        Returns:
            Volume: The retrieved volume object.
        """
        return (
            self.session.query(Volume)
            .filter_by(name=volume_name, storage_id=storage_id)
            .first()
        )

    def _delete(self, volume_id: UUID) -> None:
        """Delete a volume by its ID.

        Args:
            volume_id (UUID): The ID of the volume to delete.
        """
        self.session.query(Volume).filter_by(id=volume_id).delete()

    def _bulk_update(self, data: List[Dict]) -> None:
        """Perform a bulk update on a list of volumes.

        Args:
            data (List[Volume]): A list of volumes with updated data.
        """
        self.session.execute(update(Volume), data)
