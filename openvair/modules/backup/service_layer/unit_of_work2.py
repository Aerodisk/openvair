"""Unit of Work pattern implementation for managing database transactions.

This module defines an abstract base class and a concrete implementation
of the Unit of Work pattern using SQLAlchemy. It provides a structured
way to manage database transactions and ensure consistency.
"""

from sqlalchemy.orm import sessionmaker

from openvair.modules.backup.config import DEFAULT_SESSION_FACTORY
from openvair.common.uow.base_sqlalchemy import BaseSqlAlchemyUnitOfWork
from openvair.modules.backup.adapters.repository import SqlAlchemyRepository


class SqlAlchemyUnitOfWork(BaseSqlAlchemyUnitOfWork):
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
        super().__init__(session_factory)

    def _init_repositories(self) -> None:
        """Initializes repositories for the backup module."""
        self.repository = SqlAlchemyRepository(self.session)
