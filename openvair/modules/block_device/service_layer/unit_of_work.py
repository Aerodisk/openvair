"""Module for managing the UnitOfWork pattern in the Block Device service layer.

This module defines the `AbstractUnitOfWork` abstract base class, which provides
a common interface for managing database transactions and repository
interactions. The `SqlAlchemyUnitOfWork` class is a concrete implementation of
the `AbstractUnitOfWork` class, which uses SQLAlchemy to handle the database
operations.

The `AbstractUnitOfWork` class defines the following methods:
- `__enter__`: Enters the unit of work context, initializing the repository.
- `__exit__`: Exits the unit of work context, performing a rollback if
    necessary.
- `commit`: Commits the current database transaction.
- `rollback`: Rolls back the current database transaction.

The `SqlAlchemyUnitOfWork` class is a subclass of `AbstractUnitOfWork` that
provides the concrete implementation of the unit of work using SQLAlchemy.

Classes:
    AbstractUnitOfWork: Abstract base class for managing the Unit of Work
        pattern.
    SqlAlchemyUnitOfWork: Concrete implementation of the Unit of Work pattern
        using SQLAlchemy.
"""

from __future__ import annotations

import abc
from typing import TYPE_CHECKING, Any

from openvair.modules.block_device.config import DEFAULT_SESSION_FACTORY
from openvair.modules.block_device.adapters import repository

if TYPE_CHECKING:
    from sqlalchemy.orm import Session, sessionmaker


class AbstractUnitOfWork(metaclass=abc.ABCMeta):
    """Abstract base class for managing the Unit of Work pattern.

    This class defines the common interface for managing database transactions
    and repository interactions. Concrete implementations of this class should
    provide the specific implementation details for their respective data
    storage solutions.

    Attributes:
        interfaces (repository.AbstractRepository): The repository interface for
            interacting with the underlying data storage.
    """

    interfaces: repository.AbstractRepository

    def __enter__(self) -> AbstractUnitOfWork:
        """Enter the unit of work context, initializing the repository."""
        return self

    def __exit__(self, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Exit the unit of work context, performing a rollback if necessary."""
        self.rollback()

    @abc.abstractmethod
    def commit(self) -> None:
        """Commit the current database transaction."""
        pass

    @abc.abstractmethod
    def rollback(self) -> None:
        """Roll back the current database transaction."""
        pass


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    """Concrete implementation of the Unit of Work pattern using SQLAlchemy.

    This class provides the implementation of the Unit of Work pattern using
    SQLAlchemy as the underlying data storage solution. It inherits from the
    `AbstractUnitOfWork` class and provides the concrete implementations of the
    `commit` and `rollback` methods.

    Attributes:
        session (sqlalchemy.orm.Session): The SQLAlchemy session used for
            database transactions.
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

    def __enter__(self) -> AbstractUnitOfWork:
        """Enter the unit of work context, initializing the repository."""
        self.session = self.session_factory()
        self.interfaces = repository.SqlAlchemyRepository(self.session)
        return super().__enter__()

    def __exit__(self, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Exit the unit of work context, performing a rollback if necessary."""
        super().__exit__(*args)
        self.session.close()

    def commit(self) -> None:
        """Commit the current database transaction."""
        self.session.commit()

    def rollback(self) -> None:
        """Roll back the current database transaction."""
        self.session.rollback()
