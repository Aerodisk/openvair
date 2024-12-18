"""Unit of Work pattern implementation for managing database transactions.

This module defines an abstract base class and a concrete implementation
of the Unit of Work pattern using SQLAlchemy. It provides a structured
way to manage database transactions and ensure consistency.
"""

import abc
from typing import TYPE_CHECKING, Any

from sqlalchemy.orm import sessionmaker
from typing_extensions import Self

from openvair.modules.backup.config import DEFAULT_SESSION_FACTORY
from openvair.modules.backup.adapters.repository import SqlAlchemyRepository

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class AbstractUnitOfWork(metaclass=abc.ABCMeta):
    """Abstract base class for implementing the Unit of Work pattern.

    The Unit of Work pattern is used to group multiple operations into a single
    transactional context. This class defines the interface for entering and
    exiting the transactional context, as well as committing or rolling back
    transactions.
    """

    def __enter__(self) -> Self:
        """Enter the unit of work context.

        Returns:
            Self: The current instance of the unit of work.
        """
        return self

    def __exit__(self, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Exit the unit of work context, rolling back if necessary.

        Args:
            *args (Any): Arguments for the exit process, such as exception
                details.
        """
        self.rollback()

    @abc.abstractmethod
    def commit(self) -> None:
        """Commit the current transaction.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self) -> None:
        """Rollback the current transaction.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    """SQLAlchemy-based implementation of the Unit of Work pattern.

    This class manages database transactions using SQLAlchemy sessions.
    It ensures that transactions are properly committed, rolled back, or
    closed when the unit of work context is exited.

    Attributes:
        session_factory (sessionmaker): Factory for creating SQLAlchemy
            sessions.
        session (Session): The active SQLAlchemy session for the current unit
            of work.
        repository (SqlAlchemyRepository): Repository instance tied to the
            current session.
    """

    def __init__(
        self, session_factory: sessionmaker = DEFAULT_SESSION_FACTORY,
    ) -> None:
        """Initialize the SQLAlchemyUnitOfWork.

        Args:
            session_factory (sessionmaker, optional): Factory for creating
                SQLAlchemy sessions. Defaults to `DEFAULT_SESSION_FACTORY`.
        """
        self.session_factory = session_factory
        self.session: Session

    def __enter__(self) -> Self:
        """Enter the unit of work context.

        Creates a new SQLAlchemy session and binds a repository to it.

        Returns:
            Self: The current instance of the unit of work.
        """
        self.session = self.session_factory()
        self.repository = SqlAlchemyRepository(self.session)
        return super().__enter__()

    def __exit__(self, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Exit the unit of work context, rolling back and closing the session.

        Args:
            *args (Any): Arguments for the exit process, such as exception
                details.
        """
        super().__exit__(*args)
        self.session.close()

    def commit(self) -> None:
        """Commit the current transaction."""
        self.session.commit()

    def rollback(self) -> None:
        """Rollback the current transaction."""
        self.session.rollback()
