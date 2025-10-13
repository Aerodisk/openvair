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

from uuid import UUID
from typing import TYPE_CHECKING

from sqlalchemy import update
from sqlalchemy.orm import joinedload

from openvair.modules.image.adapters.orm import Image
from openvair.common.repositories.base_sqlalchemy import (
    BaseSqlAlchemyRepository,
)

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class ImageSqlAlchemyRepository(BaseSqlAlchemyRepository[Image]):
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
        super().__init__(session, Image)

    def get_by_name(self, image_name: str) -> list[Image]:
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

    def get_all_by_storage(self, storage_id: UUID) -> list[Image]:
        """Retrieve all images associated with a specific storage.

        Args:
            storage_id (UUID): The storage ID to filter images by.

        Returns:
            List[Image]: A list of images associated with the given storage ID.
        """
        return (
            self.session.query(Image)
            .options(joinedload(Image.attachments))
            .filter_by(storage_id=storage_id)
            .all()
        )

    def bulk_update(self, data: list) -> None:
        """Perform a bulk update on images.

        Args:
            data (List): A list of dictionaries containing the update data.
        """
        self.session.execute(update(Image), data)
