"""Unit of Work pattern implementation for user management.

This module defines a SQLAlchemy-based Unit of Work for managing database
transactions and repositories.

Classes:
    UserSqlAlchemyUnitOfWork: Unit of Work for the User module.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from openvair.modules.user.config import DEFAULT_SESSION_FACTORY
from openvair.modules.user.adapters import repository
from openvair.common.uow.base_sqlalchemy import BaseSqlAlchemyUnitOfWork

if TYPE_CHECKING:
    from sqlalchemy.orm import sessionmaker


class UserSqlAlchemyUnitOfWork(BaseSqlAlchemyUnitOfWork):
    """Unit of Work for User module.

    This class manages database transactions for users, ensuring consistency
    by committing or rolling back operations.

    Attributes:
        users (UserSqlAlchemyRepository): Repository for user entities.
    """

    def __init__(self, session_factory: sessionmaker = DEFAULT_SESSION_FACTORY):
        """Initialize the Unit of Work with a session factory.

        Args:
            session_factory (sessionmaker): The SQLAlchemy session factory to
                use. Defaults to DEFAULT_SESSION_FACTORY.
        """
        super().__init__(session_factory)

    def _init_repositories(self) -> None:
        """Initializes repositories for the user module."""
        self.users = repository.UserSqlAlchemyRepository(self.session)
