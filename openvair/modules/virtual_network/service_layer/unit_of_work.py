"""Unit of Work pattern implementation for virtual network management.

This module defines the abstract base class and its SQLAlchemy-based
implementation for managing the lifecycle of database operations related to
virtual networks.

Classes:
    - AbstractUnitOfWork: Abstract base class for unit of work pattern.
    - SqlAlchemyUnitOfWork: SQLAlchemy implementation of the unit of work
        pattern for virtual networks.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from openvair.common.uow.base_sqlalchemy import BaseSqlAlchemyUnitOfWork
from openvair.modules.virtual_network.config import DEFAULT_SESSION_FACTORY
from openvair.modules.virtual_network.adapters import repository

if TYPE_CHECKING:
    from sqlalchemy.orm import sessionmaker


class VirtualNetworkSqlAlchemyUnitOfWork(BaseSqlAlchemyUnitOfWork):
    """SQLAlchemy-based implementation of the unit of work pattern.

    This class manages the lifecycle of database operations using SQLAlchemy,
    ensuring that all changes to virtual network-related entities are committed
    or rolled back as a single unit of work.

    Attributes:
        virtual_networks (VirtualNetworkSqlAlchemyRepository): Repository
            for virtual network entities.
    """

    def __init__(self, session_factory: sessionmaker = DEFAULT_SESSION_FACTORY):
        """Initialize the SqlAlchemyUnitOfWork with a session factory.

        Args:
            session_factory (sessionmaker): SQLAlchemy session factory.
        """
        super().__init__(session_factory)

    def _init_repositories(self) -> None:
        """Initializes repositories for the virtual network module."""
        self.virtual_networks = repository.VirtualNetworkSqlAlchemyRepository(
            self.session
        )
