"""Module for unit of work pattern implementation.

This module defines the `AbstractUnitOfWork` and `SqlAlchemyUnitOfWork` classes,
which manage database transactions using the unit of work pattern. The
`SqlAlchemyUnitOfWork` class provides a concrete implementation with SQLAlchemy.

Classes:
    AbstractUnitOfWork: Abstract base class for unit of work pattern.
    SqlAlchemyUnitOfWork: Concrete implementation of AbstractUnitOfWork using
        SQLAlchemy.
"""

from __future__ import annotations

import abc
from typing import TYPE_CHECKING, Any

from openvair.modules.event_store.config import DEFAULT_SESSION_FACTORY
from openvair.modules.event_store.adapters import repository

if TYPE_CHECKING:
    from sqlalchemy.orm import Session, sessionmaker


class AbstractUnitOfWork(metaclass=abc.ABCMeta):
    """Abstract base class for unit of work pattern.

    This class defines the interface for unit of work implementations, managing
    database transactions and repositories.
    """

    events: repository.AbstractRepository

    def __enter__(self) -> AbstractUnitOfWork:
        """Enter the runtime context related to this object.

        Returns:
            AbstractUnitOfWork: The unit of work instance.
        """
        return self

    def __exit__(self, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Exit the runtime context related to this object.

        This method rolls back the transaction if any exception occurred.
        """
        self.rollback()

    @abc.abstractmethod
    def commit(self) -> None:
        """Commit the transaction.

        This method should be implemented to commit the current transaction.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self) -> None:
        """Rollback the transaction.

        This method should be implemented to rollback the current transaction.
        """
        raise NotImplementedError


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    """Concrete implementation of AbstractUnitOfWork using SQLAlchemy.

    This class manages database transactions using SQLAlchemy's session factory.
    """

    def __init__(self, session_factory: sessionmaker = DEFAULT_SESSION_FACTORY):
        """Initialize the SqlAlchemyUnitOfWork instance.

        Args:
            session_factory (sessionmaker): The SQLAlchemy session factory to
                use. Defaults to DEFAULT_SESSION_FACTORY.
        """
        self.session_factory = session_factory
        self.session: Session

    def __enter__(self) -> AbstractUnitOfWork:
        """Enter the runtime context related to this object.

        This method initializes a new SQLAlchemy session and repository.

        Returns:
            SqlAlchemyUnitOfWork: The unit of work instance.
        """
        self.session = self.session_factory()
        self.events = repository.SqlAlchemyRepository(self.session)
        return super(SqlAlchemyUnitOfWork, self).__enter__()

    def __exit__(self, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Exit the runtime context related to this object.

        This method closes the SQLAlchemy session.
        """
        super(SqlAlchemyUnitOfWork, self).__exit__(*args)
        self.session.close()

    def commit(self) -> None:
        """Commit the transaction.

        This method commits the current SQLAlchemy session transaction.
        """
        self.session.commit()

    def rollback(self) -> None:
        """Rollback the transaction.

        This method rolls back the current SQLAlchemy session transaction.
        """
        self.session.rollback()
