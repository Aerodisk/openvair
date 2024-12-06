"""Module for unit of work pattern in virtual machines service layer.

This module provides an implementation of the unit of work pattern for
managing transactions in the virtual machines service layer. The unit of work
pattern ensures that a series of operations on the repository are completed
within a single transaction, providing a mechanism to commit or roll back
the changes as needed.

Classes:
    AbstractUnitOfWork: Abstract base class defining the interface for a
        unit of work.
    SqlAlchemyUnitOfWork: Concrete implementation of the unit of work
        pattern using SQLAlchemy for managing database transactions.
"""

from __future__ import annotations

import abc
from typing import TYPE_CHECKING, Any

from typing_extensions import Self

from openvair.modules.virtual_machines.config import DEFAULT_SESSION_FACTORY
from openvair.modules.virtual_machines.adapters import repository

if TYPE_CHECKING:
    from sqlalchemy.orm import Session, sessionmaker


class AbstractUnitOfWork(metaclass=abc.ABCMeta):
    """Abstract base class for unit of work pattern.

    This class defines the interface for a unit of work, which manages
    transactions and provides methods to commit or roll back changes.
    It ensures that a series of operations on the repository are completed
    within a single transaction.

    Attributes:
        virtual_machines (repository.AbstractRepository): The repository
            for managing virtual machines.
    """

    virtual_machines: repository.AbstractRepository

    @abc.abstractmethod
    def __enter__(self) -> AbstractUnitOfWork:
        """Enter the runtime context related to this object.

        Returns:
            AbstractUnitOfWork: The unit of work instance.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def __exit__(self, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Exit the runtime context related to this object."""
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
    """SQLAlchemy-based implementation of the unit of work pattern.

    This class provides an implementation of the unit of work pattern using
    SQLAlchemy for managing database transactions. It ensures that a series
    of operations on the virtual machines repository are performed within
    a single transaction.

    Attributes:
        session_factory (sessionmaker): The SQLAlchemy session factory.
        session (Session): The current SQLAlchemy session.
    """

    def __init__(self, session_factory: sessionmaker = DEFAULT_SESSION_FACTORY):
        """Initialize the SqlAlchemyUnitOfWork with a session factory.

        Args:
            session_factory (sessionmaker): The SQLAlchemy session factory.
        """
        self.session_factory = session_factory
        self.session: Session

    def __enter__(self) -> Self:
        """Enter the runtime context related to this object.

        This method opens a new SQLAlchemy session and sets up the virtual
        machines repository.

        Returns:
            SqlAlchemyUnitOfWork: The unit of work instance.
        """
        self.session = self.session_factory()
        self.virtual_machines = repository.SqlAlchemyRepository(self.session)
        return self

    def __exit__(self, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Exit the runtime context related to this object.

        This method rolls back the transaction if necessary and closes the
        SQLAlchemy session.
        """
        super().__exit__(*args)
        self.session.close()

    def commit(self) -> None:
        """Commit the transaction."""
        self.session.commit()

    def rollback(self) -> None:
        """Roll back the transaction."""
        self.session.rollback()
