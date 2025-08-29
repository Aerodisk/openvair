"""Unit of Work implementation for managing database transactions.

This module defines a class BackupSqlAlchemyUnitOfWork whitch implements
BaseSqlAlchemyUnitOfWork.
"""

from sqlalchemy.orm import sessionmaker

from openvair.modules.backup.config import DEFAULT_SESSION_FACTORY
from openvair.common.uow.base_sqlalchemy import BaseSqlAlchemyUnitOfWork
from openvair.modules.backup.adapters.repository import (
    BackupSqlAlchemyRepository,
)


class BackupSqlAlchemyUnitOfWork(BaseSqlAlchemyUnitOfWork):
    """SQLAlchemy-based implementation of the Unit of Work pattern for Backup.

    This class manages database transactions using SQLAlchemy sessions.
    It ensures that transactions are properly committed, rolled back, or
    closed when the unit of work context is exited.

    Attributes:
        session_factory (sessionmaker): Factory for creating SQLAlchemy
            sessions.
        session (Session): The active SQLAlchemy session for the current unit
            of work.
        repository (BackupSqlAlchemyRepository): Repository instance tied to the
            current session.
    """

    def __init__(
        self,
        session_factory: sessionmaker = DEFAULT_SESSION_FACTORY,
    ) -> None:
        """Initialize the SQLAlchemyUnitOfWork.

        Args:
            session_factory (sessionmaker, optional): Factory for creating
                SQLAlchemy sessions. Defaults to `DEFAULT_SESSION_FACTORY`.
        """
        super().__init__(session_factory)

    def _init_repositories(self) -> None:
        """Initializes repositories for the backup module."""
        self.repository = BackupSqlAlchemyRepository(self.session)
