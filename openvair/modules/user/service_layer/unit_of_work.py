"""Unit of Work pattern implementation for user management.

This module defines an abstract base class and a SQLAlchemy-based concrete
implementation of the Unit of Work pattern. The Unit of Work pattern helps
manage database transactions and ensures that all operations within a
transaction are completed successfully before committing.

Classes:
    AbstractUnitOfWork: Abstract base class defining the Unit of Work interface.
    SqlAlchemyUnitOfWork: Concrete implementation of the Unit of Work interface
        using SQLAlchemy for database transactions.
"""

from __future__ import annotations

import abc
from typing import TYPE_CHECKING, Any

from openvair.modules.user.config import DEFAULT_SESSION_FACTORY
from openvair.modules.user.adapters import repository

if TYPE_CHECKING:
    from sqlalchemy.orm import Session, sessionmaker


class AbstractUnitOfWork(metaclass=abc.ABCMeta):
    """Abstract base class for the Unit of Work pattern.

    This class defines the interface for managing database transactions
    within a unit of work. Subclasses must implement the methods for
    committing, rolling back, and entering/exiting the unit of work.
    """

    users: repository.AbstractRepository

    def __enter__(self) -> AbstractUnitOfWork:
        """Enter the runtime context related to this object.

        Returns:
            AbstractUnitOfWork: The instance of the Unit of Work.
        """
        return self

    def __exit__(self, *args: Any) -> None: # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Exit the runtime context and rollback if necessary.

        Args:
            *args: Variable length argument list for context exit handling.
        """
        self.rollback()

    @abc.abstractmethod
    def commit(self) -> None:
        """Commit the transaction."""
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self) -> None:
        """Rollback the transaction."""
        raise NotImplementedError


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    """SQLAlchemy-based implementation of the Unit of Work pattern.

    This class manages database transactions using SQLAlchemy and provides
    concrete implementations of the methods defined in AbstractUnitOfWork.
    """

    def __init__(self, session_factory: sessionmaker = DEFAULT_SESSION_FACTORY):
        """Initialize the SqlAlchemyUnitOfWork with a session factory.

        Args:
            session_factory (sessionmaker): The SQLAlchemy session factory to
                use.
        """
        self.session_factory = session_factory
        self.session: Session

    def __enter__(self) -> AbstractUnitOfWork:
        """Enter the runtime context related to this object.

        This method initializes the SQLAlchemy session and repository, and
        returns the instance of the Unit of Work.

        Returns:
            SqlAlchemyUnitOfWork: The instance of the Unit of Work.
        """
        self.session = self.session_factory()
        self.users = repository.SqlAlchemyRepository(self.session)
        return super().__enter__()

    def __exit__(self, *args: Any) -> None: # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Exit the runtime context and close the session.

        This method ensures that the session is closed after the transaction
        is complete, and it calls the parent class's __exit__ method to
        handle any necessary rollback.

        Args:
            *args: Variable length argument list for context exit handling.
        """
        super().__exit__(*args)
        self.session.close()

    def commit(self) -> None:
        """Commit the current transaction."""
        self.session.commit()

    def rollback(self) -> None:
        """Rollback the current transaction."""
        self.session.rollback()
