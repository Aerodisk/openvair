"""Unit of Work pattern for storage service layer.

This module defines the Unit of Work (UoW) pattern, which manages database
transactions for storage operations. It ensures that all operations related
to a storage entity are completed successfully before committing the changes
to the database.

Classes:
    AbstractUnitOfWork: Abstract base class defining the Unit of Work interface.
    SqlAlchemyUnitOfWork: Concrete implementation of the Unit of Work using
        SQLAlchemy.
"""

from __future__ import annotations

import abc
from typing import TYPE_CHECKING, Any

from typing_extensions import Self

from openvair.modules.storage.config import DEFAULT_SESSION_FACTORY
from openvair.modules.storage.adapters import repository

if TYPE_CHECKING:
    from sqlalchemy.orm import Session, sessionmaker


class AbstractUnitOfWork(metaclass=abc.ABCMeta):
    """Abstract base class for the Unit of Work pattern.

    This class defines the interface that must be implemented by concrete
    Unit of Work classes. It ensures that all storage-related operations
    are managed within a single transaction.

    Attributes:
        storages (repository.AbstractRepository): Repository for storage
            entities.
        storage_extra_specs (repository.AbstractRepository): Repository for
            storage extra specifications.
    """

    storages: repository.AbstractRepository
    storage_extra_specs: repository.AbstractRepository

    @abc.abstractmethod
    def __enter__(self) -> AbstractUnitOfWork:
        """Enter the Unit of Work context, starting a new transaction.

        Returns:
            AbstractUnitOfWork: The current instance of the Unit of Work.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def __exit__(self, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Exit the Unit of Work context, rolling back any uncommitted changes.

        Args:
            *args: Variable length argument list for any exception information.
        """
        self.rollback()

    @abc.abstractmethod
    def commit(self) -> None:
        """Commit the current transaction."""
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self) -> None:
        """Rollback the current transaction."""
        raise NotImplementedError


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    """Concrete implementation of the Unit of Work pattern using SQLAlchemy.

    This class manages database transactions for storage operations using
    SQLAlchemy. It ensures that all operations are either fully completed or
    fully rolled back in case of errors.

    Attributes:
        session_factory (sessionmaker): A factory for creating new SQLAlchemy
            sessions.
        session (Session): The current SQLAlchemy session.
    """

    def __init__(self, session_factory: sessionmaker = DEFAULT_SESSION_FACTORY):
        """Initialize the Unit of Work with a session factory.

        Args:
            session_factory (sessionmaker): A factory for creating new
                SQLAlchemy sessions. Defaults to DEFAULT_SESSION_FACTORY.
        """
        self.session_factory = session_factory
        self.session: Session

    def __enter__(self) -> Self:
        """Enter the Unit of Work context, starting a new SQLAlchemy session.

        Returns:
            SqlAlchemyUnitOfWork: The current instance of the Unit of Work.
        """
        self.session = self.session_factory()
        self.storages = repository.SqlAlchemyRepository(self.session)
        return self

    def __exit__(self, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Exit the Unit of Work context, rolling back and closing the session.

        Args:
            *args: Variable length argument list for any exception information.
        """
        super().__exit__(*args)
        self.session.close()

    def commit(self) -> None:
        """Commit the current transaction."""
        self.session.commit()

    def rollback(self) -> None:
        """Rollback the current transaction."""
        self.session.rollback()
