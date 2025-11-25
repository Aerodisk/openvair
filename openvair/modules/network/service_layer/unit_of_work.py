"""Unit of Work pattern implementation for network operations.

This module provides an implementation of the Unit of Work pattern
for managing transactions related to network operations, using SQLAlchemy
as the underlying ORM.

Classes:
    AbstractUnitOfWork: Abstract base class defining the interface for unit of
        work.
    SqlAlchemyUnitOfWork: SQLAlchemy implementation of the unit of work pattern.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from openvair.modules.network.config import DEFAULT_SESSION_FACTORY
from openvair.modules.network.adapters import repository
from openvair.common.uow.base_sqlalchemy import BaseSqlAlchemyUnitOfWork

if TYPE_CHECKING:
    from sqlalchemy.orm import sessionmaker


class NetworkSqlAlchemyUnitOfWork(BaseSqlAlchemyUnitOfWork):
    """SQLAlchemy implementation of the unit of work pattern.

    This class provides an implementation of the Unit of Work pattern using
    SQLAlchemy, managing transactions for network operations.

    Attributes:
        interfaces (NetworkSqlAlchemyRepository): Repository for interface
            entities.
    """

    def __init__(self, session_factory: sessionmaker = DEFAULT_SESSION_FACTORY):
        """Initialize the SqlAlchemyUnitOfWork with a session factory.

        Args:
            session_factory (sessionmaker, optional): The SQLAlchemy session
                factory to use for creating sessions. Defaults to
                DEFAULT_SESSION_FACTORY.
        """
        super().__init__(session_factory)

    def _init_repositories(self) -> None:
        """Initializes repositories for the network module."""
        self.interfaces = repository.NetworkSqlAlchemyRepository(self.session)
