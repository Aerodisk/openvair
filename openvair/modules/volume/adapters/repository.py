"""Repository pattern for volume-related database operations.

This module defines the repository pattern for managing volume-related data.
It abstracts the database operations for volumes, making it easier to interact
with the database while keeping the business logic separate.

Classes:
    AbstractRepository: Abstract base class for the volume repository.
    SqlAlchemyRepository: Concrete implementation of the repository using
        SQLAlchemy.
"""

from typing import TYPE_CHECKING

from sqlalchemy import update

from openvair.modules.volume.adapters.orm import Volume
from openvair.common.repositories.base_sqlalchemy import (
    BaseSqlAlchemyRepository,
)

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class VolumeSqlAlchemyRepository(BaseSqlAlchemyRepository[Volume]):
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
        super().__init__(session, Volume)

    def get_all_by_storage(self, storage_id: str) -> list[Volume]:
        """Retrieve all volumes associated with a specific storage.

        Args:
            storage_id (str): The ID of the storage.

        Returns:
            List[Volume]: A list of volumes associated with the specified
                storage.
        """
        return self.session.query(Volume).filter_by(storage_id=storage_id).all()

    def get_by_name_and_storage(
        self,
        volume_name: str,
        storage_id: str,
    ) -> Volume | None:
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

    def bulk_update(self, data: list[dict]) -> None:
        """Perform a bulk update on a list of volumes.

        Args:
            data (List[Volume]): A list of volumes with updated data.
        """
        self.session.execute(update(Volume), data)
