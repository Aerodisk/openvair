"""Unit of Work implementation for the event_store module.

This module defines a SQLAlchemy-based Unit of Work for managing
event-related transactions and repositories.

Classes:
    - EventStoreSqlAlchemyUnitOfWork: Unit of Work for the event_store module.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from openvair.common.uow.base_sqlalchemy import BaseSqlAlchemyUnitOfWork
from openvair.modules.event_store.config import DEFAULT_SESSION_FACTORY
from openvair.modules.event_store.adapters import repository

if TYPE_CHECKING:
    from sqlalchemy.orm import sessionmaker


class EventStoreSqlAlchemyUnitOfWork(BaseSqlAlchemyUnitOfWork):
    """Unit of Work for the event_store module.

    This class manages database transactions for events, ensuring consistency
    by committing or rolling back operations.

    Attributes:
        events (EventStoreSqlAlchemyRepository): Repository for eventstore
            entities.
    """

    def __init__(
        self, session_factory: sessionmaker = DEFAULT_SESSION_FACTORY
    ) -> None:
        """Initializes the Unit of Work with a session factory.

        Args:
            session_factory (sessionmaker): SQLAlchemy session factory.
                Defaults to DEFAULT_SESSION_FACTORY.
        """
        super().__init__(session_factory)

    def _init_repositories(self) -> None:
        """Initializes repositories for the event_store module."""
        self.events = repository.EventStoreSqlAlchemyRepository(self.session)
