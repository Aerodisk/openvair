"""Unit of Work pattern implementation for network operations.

This module provides an implementation of the Unit of Work pattern
for managing transactions related to network operations, using SQLAlchemy
as the underlying ORM.

Classes:
    AbstractUnitOfWork: Abstract base class defining the interface for unit of
        work.
    SqlAlchemyUnitOfWork: SQLAlchemy implementation of the unit of work pattern.
"""

from __future__ import annotations

import abc
from typing import TYPE_CHECKING

from openvair.modules.network.config import DEFAULT_SESSION_FACTORY
from openvair.modules.network.adapters import repository

if TYPE_CHECKING:
    from sqlalchemy.orm import Session, sessionmaker


class AbstractUnitOfWork(metaclass=abc.ABCMeta):
    """Abstract base class defining the interface for unit of work.

    This class provides the interface for implementing the Unit of Work
    pattern, including methods for committing and rolling back transactions,
    as well as entering and exiting the unit of work context.
    """

    interfaces: repository.AbstractRepository
    interface_extra_specs: repository.AbstractRepository

    def __enter__(self) -> AbstractUnitOfWork:
        """Enter the unit of work context."""
        return self

    def __exit__(self, *args):
        """Exit the unit of work context, rolling back if necessary."""
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
    """SQLAlchemy implementation of the unit of work pattern.

    This class provides an implementation of the Unit of Work pattern using
    SQLAlchemy, managing transactions for network operations.

    Attributes:
        session (Session): The SQLAlchemy session used for database operations.
    """

    def __init__(self, session_factory: sessionmaker = DEFAULT_SESSION_FACTORY):
        """Initialize the SqlAlchemyUnitOfWork with a session factory.

        Args:
            session_factory (sessionmaker, optional): The SQLAlchemy session
                factory to use for creating sessions. Defaults to
                DEFAULT_SESSION_FACTORY.
        """
        self.session_factory = session_factory
        self.session = None

    def __enter__(self):
        """Enter the unit of work context, initializing repositories."""
        self.session: Session = self.session_factory()
        self.interfaces = repository.SqlAlchemyRepository(self.session)
        return super(SqlAlchemyUnitOfWork, self).__enter__()

    def __exit__(self, *args):
        """Exit the unit of work context, closing the session."""
        super(SqlAlchemyUnitOfWork, self).__exit__(*args)
        self.session.close()

    def commit(self) -> None:
        """Commit the current transaction."""
        self.session.commit()

    def rollback(self) -> None:
        """Rollback the current transaction."""
        self.session.rollback()
