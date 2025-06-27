"""Module for unit of work pattern implementation.

This module defines the `AbstractUnitOfWork` and `SqlAlchemyUnitOfWork` classes,
which manage database transactions using the unit of work pattern. The
`SqlAlchemyUnitOfWork` class provides a concrete implementation with SQLAlchemy.

Classes:
    AbstractUnitOfWork: Abstract base class for unit of work pattern.
    SqlAlchemyUnitOfWork: Concrete implementation of AbstractUnitOfWork using
        SQLAlchemy.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from openvair.common.uow.base_sqlalchemy import BaseSqlAlchemyUnitOfWork
from openvair.modules.event_store.config import DEFAULT_SESSION_FACTORY
from openvair.modules.event_store.adapters import repository

if TYPE_CHECKING:
    from sqlalchemy.orm import sessionmaker


class EventstoreSqlAlchemyUnitOfWork(BaseSqlAlchemyUnitOfWork):
    """Some description"""

    def __init__(
        self, session_factory: sessionmaker = DEFAULT_SESSION_FACTORY
    ) -> None:
        """Some description"""
        super().__init__(session_factory)

    def _init_repositories(self) -> None:
        """Initializes repositories for the event_store module."""
        self.events = repository.SqlAlchemyRepository(self.session)
