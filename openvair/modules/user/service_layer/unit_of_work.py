"""Unit of Work pattern implementation for user management.

This module defines an abstract base class and a SQLAlchemy-based concrete
implementation of the Unit of Work pattern. The Unit of Work pattern helps
manage database transactions and ensures that all operations within a
transaction are completed successfully before committing.

Classes:
    AbstractUnitOfWork: Abstract base class defining the Unit of Work interface.
    SqlAlchemyUnitOfWork: Concrete implementation of the Unit of Work interface
        using SQLAlchemy for database transactions.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from openvair.modules.user.config import DEFAULT_SESSION_FACTORY
from openvair.modules.user.adapters import repository
from openvair.common.uow.base_sqlalchemy import BaseSqlAlchemyUnitOfWork

if TYPE_CHECKING:
    from sqlalchemy.orm import sessionmaker

class UserSqlAlchemyUnitOfWork(BaseSqlAlchemyUnitOfWork):
    """SQLAlchemy-based implementation of the Unit of Work pattern.

    This class manages database transactions using SQLAlchemy and provides
    concrete implementations of the methods defined in AbstractUnitOfWork.
    """

    def __init__(self, session_factory: sessionmaker = DEFAULT_SESSION_FACTORY):
        """Initialize the SqlAlchemyUnitOfWork with a session factory.

        Args:
            session_factory (sessionmaker): The SQLAlchemy session factory to
                use.
        """
        super().__init__(session_factory)

    def _init_repositories(self) -> None:
        """Initializes repositories for the template module."""
        self.users = repository.SqlAlchemyRepository(self.session)

