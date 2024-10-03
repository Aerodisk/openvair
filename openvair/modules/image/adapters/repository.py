"""Module for image repository management using the Repository pattern.

This module provides an abstract repository interface for managing image-related
operations, along with a concrete implementation using SQLAlchemy. The
repository handles common image-related CRUD operations and ensures proper
database connection handling.

Classes:
    AbstractRepository: Abstract base class defining the repository interface
        for image management.
    SqlAlchemyRepository: Concrete implementation of AbstractRepository using
        SQLAlchemy for database operations.
"""

import abc
from uuid import UUID
from typing import TYPE_CHECKING, List

from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import joinedload

from openvair.modules.image.adapters.orm import Image
from openvair.modules.image.adapters.exceptions import DBCannotBeConnectedError

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class AbstractRepository(metaclass=abc.ABCMeta):
    """Abstract base class for the image repository.

    This class defines the interface for interacting with image data in the
    repository. Subclasses must provide implementations for all abstract
    methods.
    """

    def _check_connection(self) -> None:
        """Check the database connection.

        Raises:
            NotImplementedError: This method should be implemented by
                subclasses.
        """
        raise NotImplementedError

    # Image

    def add(self, image: Image) -> None:
        """Add a new image to the repository.

        Args:
            image (Image): The image entity to add.
        """
        self._add(image)

    def get(self, image_id: UUID) -> Image:
        """Retrieve an image by its ID.

        Args:
            image_id (UUID): The unique identifier of the image.

        Returns:
            Image: The image entity matching the given ID.
        """
        return self._get(image_id)

    def get_by_name(self, image_name: str) -> List[Image]:
        """Retrieve images by their name.

        Args:
            image_name (str): The name of the images to retrieve.

        Returns:
            List[Image]: A list of images matching the given name.
        """
        return self._get_by_name(image_name)

    def get_all(self) -> List[Image]:
        """Retrieve all images from the repository.

        Returns:
            List[Image]: A list of all images in the repository.
        """
        return self._get_all()

    def get_all_by_storage(self, storage_id: str) -> List[Image]:
        """Retrieve all images associated with a specific storage.

        Args:
            storage_id (str): The storage ID to filter images by.

        Returns:
            List[Image]: A list of images associated with the given storage ID.
        """
        return self._get_all_by_storage(storage_id)

    def delete(self, image_id: UUID) -> None:
        """Delete an image by its ID.

        Args:
            image_id (UUID): The unique identifier of the image to delete.
        """
        self._delete(image_id)

    def bulk_update(self, data: List) -> None:
        """Perform a bulk update on images.

        Args:
            data (List): A list of dictionaries containing the update data.
        """
        self._bulk_update(data)

    @abc.abstractmethod
    def _add(self, image: Image) -> None:
        """Add a new image to the repository.

        Args:
            image (Image): The image entity to add.

        Raises:
            NotImplementedError: This method should be implemented by
                subclasses.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _get(self, image_id: UUID) -> Image:
        """Retrieve an image by its ID.

        Args:
            image_id (UUID): The unique identifier of the image.

        Returns:
            Image: The image entity matching the given ID.

        Raises:
            NotImplementedError: This method should be implemented by
                subclasses.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _get_by_name(self, image_name: str) -> List[Image]:
        """Retrieve images by their name.

        Args:
            image_name (str): The name of the images to retrieve.

        Returns:
            List[Image]: A list of images matching the given name.

        Raises:
            NotImplementedError: This method should be implemented by
                subclasses.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _get_all(self) -> List[Image]:
        """Retrieve all images from the repository.

        Returns:
            List[Image]: A list of all images in the repository.

        Raises:
            NotImplementedError: This method should be implemented by
                subclasses.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _get_all_by_storage(self, storage_id: str) -> List[Image]:
        """Retrieve all images associated with a specific storage.

        Args:
            storage_id (str): The storage ID to filter images by.

        Returns:
            List[Image]: A list of images associated with the given storage ID.

        Raises:
            NotImplementedError: This method should be implemented by
                subclasses.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _delete(self, image_id: UUID) -> None:
        """Delete an image by its ID.

        Args:
            image_id (UUID): The unique identifier of the image to delete.

        Raises:
            NotImplementedError: This method should be implemented by
                subclasses.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _bulk_update(self, data: List) -> None:
        """Perform a bulk update on images.

        Args:
            data (List): A list of dictionaries containing the update data.

        Raises:
            NotImplementedError: This method should be implemented by
                subclasses.
        """
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    """SQLAlchemy-based implementation of the AbstractRepository.

    This class provides concrete implementations of the image repository
    interface using SQLAlchemy for database operations.
    """

    def __init__(self, session: 'Session'):
        """Initialize the SqlAlchemyRepository with a database session.

        Args:
            session (Session): The SQLAlchemy session to use for database
                operations.
        """
        super(SqlAlchemyRepository, self).__init__()
        self.session: Session = session
        self._check_connection()

    def _check_connection(self) -> None:
        """Check the database connection.

        This method attempts to establish a connection to the database
        and raises a `DBCannotBeConnectedError` if the connection fails.

        Raises:
            DBCannotBeConnectedError: If the database connection cannot be
                established.
        """
        try:
            self.session.connection()
        except OperationalError:
            raise DBCannotBeConnectedError(message="Can't connect to Database")

    def _get(self, image_id: UUID) -> Image:
        """Retrieve an image by its ID.

        Args:
            image_id (UUID): The unique identifier of the image.

        Returns:
            Image: The image entity matching the given ID.
        """
        return (
            self.session.query(Image)
            .options(joinedload(Image.attachments))
            .filter_by(id=image_id)
            .one()
        )

    def _get_by_name(self, image_name: str) -> List[Image]:
        """Retrieve images by their name.

        Args:
            image_name (str): The name of the images to retrieve.

        Returns:
            List[Image]: A list of images matching the given name.
        """
        return (
            self.session.query(Image)
            .options(joinedload(Image.attachments))
            .filter_by(name=image_name)
            .all()
        )

    def _add(self, image: Image) -> None:
        """Add a new image to the repository.

        Args:
            image (Image): The image entity to add.
        """
        self.session.add(image)

    def _get_all(self) -> List[Image]:
        """Retrieve all images from the repository.

        Returns:
            List[Image]: A list of all images in the repository.
        """
        return (
            self.session.query(Image)
            .options(joinedload(Image.attachments))
            .all()
        )

    def _get_all_by_storage(self, storage_id: str) -> List[Image]:
        """Retrieve all images associated with a specific storage.

        Args:
            storage_id (str): The storage ID to filter images by.

        Returns:
            List[Image]: A list of images associated with the given storage ID.
        """
        return (
            self.session.query(Image)
            .options(joinedload(Image.attachments))
            .filter_by(storage_id=storage_id)
            .all()
        )

    def _delete(self, image_id: UUID) -> None:
        """Delete an image by its ID.

        Args:
            image_id (UUID): The unique identifier of the image to delete.
        """
        return self.session.query(Image).filter_by(id=image_id).delete()

    def _bulk_update(self, data: List) -> None:
        """Perform a bulk update on images.

        Args:
            data (List): A list of dictionaries containing the update data.
        """
        self.session.bulk_update_mappings(Image, data)
