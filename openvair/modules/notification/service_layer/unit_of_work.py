"""Unit of Work pattern for the notification service layer.

This module provides the `AbstractUnitOfWork` and `SqlAlchemyUnitOfWork`
classes, which implement the Unit of Work pattern for managing database
transactions in the notification service layer.

Classes:
    - AbstractUnitOfWork: Abstract base class for the Unit of Work pattern.
    - SqlAlchemyUnitOfWork: Concrete implementation of the Unit of Work pattern
        using SQLAlchemy.
"""

from __future__ import annotations

import abc
from typing import TYPE_CHECKING

from openvair.modules.notification.config import DEFAULT_SESSION_FACTORY
from openvair.modules.notification.adapters import repository

if TYPE_CHECKING:
    from sqlalchemy.orm import Session, sessionmaker


class AbstractUnitOfWork(metaclass=abc.ABCMeta):
    """Abstract base class for the Unit of Work pattern."""

    notifications: repository.AbstractRepository

    @abc.abstractmethod
    def __enter__(self) -> AbstractUnitOfWork:
        """Enter the runtime context related to this object.

        Returns:
            AbstractUnitOfWork: The unit of work instance.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def __exit__(self, *args):
        """Exit the runtime context related to this object.

        This method is responsible for rolling back the transaction if an
        exception occurs.
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
    """SQLAlchemy-based implementation of the Unit of Work pattern."""

    def __init__(self, session_factory: sessionmaker = DEFAULT_SESSION_FACTORY):
        """Initialize the SqlAlchemyUnitOfWork.

        Args:
            session_factory (sessionmaker): The session factory to use for
                creating sessions. Defaults to DEFAULT_SESSION_FACTORY.
        """
        self.session_factory = session_factory
        self.session = None

    def __enter__(self):
        """Enter the runtime context related to this object.

        This method creates a new session and sets up the notifications
        repository.

        Returns:
            SqlAlchemyUnitOfWork: The unit of work instance.
        """
        self.session: Session = self.session_factory()
        self.notifications = repository.SqlAlchemyRepository(self.session)
        return self

    def __exit__(self, *args):
        """Exit the runtime context related to this object.

        This method closes the session and handles any exceptions by rolling
        back the transaction.
        """
        super(SqlAlchemyUnitOfWork, self).__exit__(*args)
        self.session.close()

    def commit(self) -> None:
        """Commit the transaction."""
        self.session.commit()

    def rollback(self) -> None:
        """Rollback the transaction."""
        self.session.rollback()
