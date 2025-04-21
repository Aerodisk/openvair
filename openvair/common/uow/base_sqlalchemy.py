"""Base SQLAlchemy Unit of Work implementation.

This module provides an abstract base class for Unit of Work implementations
using SQLAlchemy. It manages database sessions and ensures proper transaction
handling.

Classes:
    - BaseSqlAlchemyUnitOfWork: Base class for SQLAlchemy-based Unit of Work.
"""

import abc
from types import TracebackType
from typing import TYPE_CHECKING, Type, Optional

from sqlalchemy.orm import sessionmaker
from typing_extensions import Self

from openvair.common.uow.abstract import AbstractUnitOfWork

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class BaseSqlAlchemyUnitOfWork(AbstractUnitOfWork):
    """Abstract base class for SQLAlchemy-based Unit of Work.

    This class provides transaction management using SQLAlchemy, ensuring
    consistency by committing or rolling back database operations.
    """

    def __init__(self, session_factory: sessionmaker) -> None:
        """Initializes the Unit of Work with a session factory.

        Args:
            session_factory (sessionmaker): The SQLAlchemy session factory for
                creating database sessions.
        """
        self.session_factory = session_factory
        self.session: Session

    def __enter__(self) -> Self:
        """Begins a new database session and initializes repositories.

        Returns:
            Self: The instance of the Unit of Work.
        """
        self.session = self.session_factory()
        self._init_repositories()
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        """Handles transaction completion and cleanup.

        If an exception occurs, the transaction is rolled back; otherwise,
        resources are closed.

        Args:
            exc_type (Optional[Type[BaseException]]): The type of exception
                raised, if any.
            exc_val (Optional[BaseException]): The exception instance, if any.
            exc_tb (Optional[TracebackType]): The traceback of the exception,
                if any.
        """
        if exc_type:
            self.rollback()
        self.session.close()

    @abc.abstractmethod
    def _init_repositories(self) -> None:
        """Initializes repositories for data access.

        This method should be implemented in subclasses to set up specific
        repository instances.
        """
        ...

    def commit(self) -> None:
        """Commits the current transaction, persisting changes to the db."""
        self.session.commit()

    def rollback(self) -> None:
        """Rolls back the current transaction.

        Discards all uncommitted changes.
        """
        self.session.rollback()
