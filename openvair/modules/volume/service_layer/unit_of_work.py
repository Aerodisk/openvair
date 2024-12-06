"""Module for handling unit of work in the volume service layer.

This module defines the abstract and concrete implementations of the Unit
of Work pattern for managing database transactions in the volume service
layer. It ensures that operations on the database are performed within a
transactional context, allowing for rollback in case of errors.

Classes:
    AbstractUnitOfWork: Abstract base class for unit of work.
    SqlAlchemyUnitOfWork: Concrete implementation of the unit of work using
        SQLAlchemy.
"""

from __future__ import annotations

import abc
from typing import TYPE_CHECKING, Any

from typing_extensions import Self

from openvair.modules.volume.config import DEFAULT_SESSION_FACTORY
from openvair.modules.volume.adapters import repository

if TYPE_CHECKING:
    from sqlalchemy.orm import Session, sessionmaker


class AbstractUnitOfWork(metaclass=abc.ABCMeta):
    """Abstract base class for unit of work in volume service layer.

    This class defines the interface for implementing the Unit of Work
    pattern, which manages the transaction boundaries for operations on
    volume-related entities.
    """

    volumes: repository.AbstractRepository

    @abc.abstractmethod
    def __enter__(self) -> AbstractUnitOfWork:
        """Enter the context, starting a new database session."""
        raise NotImplementedError

    def __exit__(self, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Exit the context and roll back the transaction if necessary."""
        self.rollback()

    @abc.abstractmethod
    def commit(self) -> None:
        """Commit the transaction."""
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self) -> None:
        """Roll back the transaction."""
        raise NotImplementedError


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    """Concrete implementation of unit of work using SQLAlchemy.

    This class provides a SQLAlchemy-based implementation of the Unit of
    Work pattern, managing the transaction boundaries for operations on
    volume-related entities.
    """

    def __init__(self, session_factory: sessionmaker = DEFAULT_SESSION_FACTORY):
        """Initialize the SqlAlchemyUnitOfWork.

        Args:
            session_factory (callable, optional): A factory function that
                returns a SQLAlchemy session.
                Defaults to `DEFAULT_SESSION_FACTORY`.
        """
        self.session_factory = session_factory
        self.session: Session

    def __enter__(self) -> Self:
        """Enter the context, starting a new database session."""
        self.session = self.session_factory()
        self.volumes = repository.SqlAlchemyRepository(self.session)
        return self

    def __exit__(self, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Exit the context, closing the session and rolling back if needed."""
        super(SqlAlchemyUnitOfWork, self).__exit__(*args)
        self.session.close()

    def commit(self) -> None:
        """Commit the current transaction."""
        self.session.commit()

    def rollback(self) -> None:
        """Roll back the current transaction."""
        self.session.rollback()
