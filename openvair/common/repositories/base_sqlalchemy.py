"""Base repository implementation using SQLAlchemy.

This module provides a concrete implementation of the AbstractRepository
interface using SQLAlchemy ORM.

Classes:
    - BaseSqlAlchemyRepository: A repository class using SQLAlchemy.
"""

from typing import List, Type, Generic, TypeVar, Optional

from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from openvair.abstracts.exceptions import DBCannotBeConnectedError
from openvair.common.repositories.abstract import AbstractRepository

T = TypeVar('T')


class BaseSqlAlchemyRepository(AbstractRepository[T], Generic[T]):
    """Base repository implementation using SQLAlchemy.

    This class provides CRUD operations for managing database entities
    using SQLAlchemy ORM.
    """

    def __init__(self, session: Session, model_cls: Type[T]) -> None:
        """Initializes the repository with a database session and model class.

        Args:
            session (Session): The SQLAlchemy session for database operations.
            model_cls (Type[T]): The model class associated with this
                repository.

        Raises:
            DBCannotBeConnectedError: If the database connection cannot be
                established.
        """
        self.session = session
        self.model_cls = model_cls
        self._check_connection()

    def _check_connection(self) -> None:
        """Checks if the database connection is available.

        Raises:
            DBCannotBeConnectedError: If the connection to the database fails.
        """
        try:
            self.session.connection()
        except OperationalError:
            message = "Can't connect to Database"
            raise DBCannotBeConnectedError(message)

    def add(self, entity: T) -> None:
        """Adds a new entity to the database.

        Args:
            entity (T): The entity to add.
        """
        self.session.add(entity)

    def get(self, entity_id: int) -> Optional[T]:
        """Retrieves an entity by its ID.

        Args:
            entity_id (int): The ID of the entity.

        Returns:
            Optional[T]: The retrieved entity or None if not found.
        """
        return self.session.query(self.model_cls).get(entity_id)

    def get_all(self) -> List[T]:
        """Retrieves all entities from the database.

        Returns:
            List[T]: A list of all stored entities.
        """
        return self.session.query(self.model_cls).all()

    def delete(self, entity_id: int) -> None:
        """Deletes an entity by its ID.

        Args:
            entity_id (int): The ID of the entity to delete.
        """
        self.session.query(self.model_cls).filter_by(id=entity_id).delete()

    def update(self, entity: T) -> None:
        """Updates an existing entity in the database.

        Args:
            entity (T): The entity with updated data.
        """
        self.session.merge(entity)
