"""Unit of Work pattern for the notification service layer.

This module provides SQLAlchemy-based Unit of Work for managing database
transactions in the notification service layer.

Classes:
    - NotificationSqlAlchemyUnitOfWork: Unit of Work for the notification
        module.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from openvair.common.uow.base_sqlalchemy import BaseSqlAlchemyUnitOfWork
from openvair.modules.notification.config import DEFAULT_SESSION_FACTORY
from openvair.modules.notification.adapters import repository

if TYPE_CHECKING:
    from sqlalchemy.orm import sessionmaker

class NotificationSqlAlchemyUnitOfWork(BaseSqlAlchemyUnitOfWork):
    """Unit of Work for the notification module.

    This class manages database transactions for notifications, ensuring
    consistency by committing or rolling back operations.

    Attributes:
        notifications (NotificationSqlAlchemyRepository): Repository for
            Notification entities.
    """

    def __init__(self, session_factory: sessionmaker = DEFAULT_SESSION_FACTORY):
        """Initializes the Unit of Work with a session factory.

        Args:
            session_factory (sessionmaker): The session factory to use for
                creating sessions. Defaults to DEFAULT_SESSION_FACTORY.
        """
        super().__init__(session_factory)

    def _init_repositories(self) -> None:
        """Initializes repositories for the notification module."""
        self.notifications = repository.NotificationSqlAlchemyRepository(
            self.session
        )
