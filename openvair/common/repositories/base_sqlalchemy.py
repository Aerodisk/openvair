"""Base repository implementation using SQLAlchemy.

This module provides a concrete implementation of the AbstractRepository
interface using SQLAlchemy ORM.

Classes:
    - BaseSqlAlchemyRepository: A repository class using SQLAlchemy.
"""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session, DeclarativeBase

from openvair.abstracts.exceptions import DBCannotBeConnectedError
from openvair.common.repositories.abstract import AbstractRepository
from openvair.common.repositories.exceptions import EntityNotFoundError


class BaseSqlAlchemyRepository[T: DeclarativeBase](AbstractRepository[T]):
    """Base repository implementation using SQLAlchemy.

    This class provides CRUD operations for managing database entities
    using SQLAlchemy ORM.
    """

    def __init__(self, session: Session, model_cls: type[T]) -> None:
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
        """Adds a new entity to the database or marks it for update if it already exists in the session.

        Args:
            entity (T): The entity to add or update.

        SQLAlchemy behavior:
            - If the entity is **new** (i.e., it doesn't exist in the current
            session and has no associated record in the database), it will be
            inserted into the database upon commit.
            - If the entity already exists in the session (i.e., it was
            previously loaded or added), it will be **updated** instead
            of inserted, and its state will be persisted upon commit.
            - This method **does not check for existence** in the database; it
            relies on the session's tracking of the object.

        Important notes:
            - If the entity is **new** (has not been added or loaded in the
            current session), it will be treated as a new entity and inserted
            into the database.
            - If the entity was **already tracked** by the session (loaded or
            added earlier), the method **updates its state** and
            commits the changes to the database without needing to explicitly
            call an update method.
        """  # noqa: E501, W505
        self.session.add(entity)
        self.session.flush()  # To populate entity.id immediately

    def get(self, entity_id: UUID) -> T | None:
        """Retrieves an entity by its ID.

        Args:
            entity_id (UUID): The ID of the entity.

        Returns:
            Optional[T]: The retrieved entity or None if not found.
        """
        return self.session.get(self.model_cls, entity_id)

    def get_or_fail(self, entity_id: UUID) -> T:
        """Retrieves an entity by its ID or raises an exception if not found.

        Args:
            entity_id (UUID): The ID of the entity.

        Returns:
            T: The retrieved entity.

        Raises:
            EntityNotFoundError: If the entity does not exist.
        """
        if (entity := self.session.get(self.model_cls, entity_id)) is None:
            msg = f'{self.model_cls.__name__} with ID {entity_id} not found.'
            raise EntityNotFoundError(msg)
        return entity

    def get_all(self) -> list[T]:
        """Retrieves all entities from the database.

        Returns:
            List[T]: A list of all stored entities.
        """
        stmt = select(self.model_cls)
        return list(self.session.scalars(stmt).all())

    def delete(self, entity: T) -> None:
        """Deletes the given entity from the database.

        Args:
            entity (T): The entity instance to delete.

        SQLAlchemy behavior:
            - Calls `session.delete(entity)`, marking it for deletion.
            - Changes are applied on `session.commit()`.
        """
        entity = self.session.merge(entity)
        self.session.delete(entity)

    def delete_by_id(self, entity_id: UUID) -> None:
        """Deletes an entity from the database by its ID.

        Args:
            entity_id (UUID): The ID of the entity to delete.

        Raises:
            EntityNotFoundError: If no entity with the given ID exists.

        SQLAlchemy behavior:
            - Performs a direct `DELETE` using `query(...).filter_by(id=...).delete()`.
            - Returns number of affected rows.
        """  # noqa: E501
        rows_deleted = (
            self.session.query(self.model_cls).filter_by(id=entity_id).delete()
        )

        if rows_deleted == 0:
            message = (
                f'{self.model_cls.__name__} with ID {entity_id} not found.'
            )
            raise EntityNotFoundError(message)

    def update(self, entity: T) -> None:
        """Updates an existing entity in the database.

        Args:
            entity (T): The entity to update.

        SQLAlchemy behavior:
            - This method calls **merge**, which performs a merge operation that
            ensures the entity is synchronized with the session.
            - If the entity **already exists** in the database (based on its
            primary key or unique constraint), it will be updated  with the
            current data from the entity passed to the method.
            - If the entity **does not exist** in the session, the method will
            create a new entity in the session and will attempt to **insert** it
            when commit is called.

        Important notes:
            - `merge` is useful when the entity was retrieved **outside of the
            current session**, or when you are unsure whether the entity already
            exists in the session.
            - This method **does not create new entities** if one with the same
            primary key already exists in the session. Instead, it updates the
            existing entity.
            - If the entity is **new** (not tracked by the session), `merge`
            will treat it as a new entity and perform an insert.

        Use case:
            - **When the entity exists in the database**, `merge` will update
            its fields. If it doesn't exist, it will insert a new
            row. This makes it useful for synchronizing detached entities (e.g.,
            entities fetched from another session or source).
        """
        self.session.merge(entity)

    def count(self) -> int:
        """Returns the number of entities in the table.

        Returns:
            int: Total count of entities.
        """
        stmt = select(func.count()).select_from(self.model_cls)
        return self.session.scalar(stmt) or 0
