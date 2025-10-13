"""Abstract Unit of Work pattern.

This module defines an abstract base class for the Unit of Work pattern,
which manages database transactions and ensures consistency by committing
or rolling back operations as a single unit.

Classes:
    - AbstractUnitOfWork: Base class defining the contract for Unit of Work
        implementations.
"""

import abc
from types import TracebackType
from typing import Self


class AbstractUnitOfWork(abc.ABC):
    """Abstract base class for Unit of Work.

    This class provides an interface for managing transactions in a structured
    way, ensuring that operations are committed or rolled back properly.
    """

    @abc.abstractmethod
    def __enter__(self) -> Self:
        """Enters the context and initializes resources.

        Returns:
            Self: The instance of the Unit of Work.
        """
        ...

    @abc.abstractmethod
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Exits the context, ensuring proper cleanup.

        If an exception occurs, the transaction should be rolled back.

        Args:
            exc_type (Optional[Type[BaseException]]): The type of exception
                raised, if any.
            exc_val (Optional[BaseException]): The exception instance, if any.
            exc_tb (Optional[TracebackType]): The traceback of the exception,
                if any.
        """
        ...

    @abc.abstractmethod
    def _init_repositories(self) -> None:
        """Initializes repository instances.

        This method should be implemented in subclasses to set up repositories
        for data persistence.
        """
        ...

    @abc.abstractmethod
    def commit(self) -> None:
        """Commits the transaction, persisting all changes."""
        ...

    @abc.abstractmethod
    def rollback(self) -> None:
        """Rolls back the transaction, discarding all uncommitted changes."""
        ...
