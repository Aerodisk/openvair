"""Module for unit of work pattern in virtual machines service layer.

This module provides an implementation of the unit of work pattern for
managing transactions in the virtual machines service layer. The unit of work
pattern ensures that a series of operations on the repository are completed
within a single transaction, providing a mechanism to commit or roll back
the changes as needed.

Classes:
    AbstractUnitOfWork: Abstract base class defining the interface for a
        unit of work.
    SqlAlchemyUnitOfWork: Concrete implementation of the unit of work
        pattern using SQLAlchemy for managing database transactions.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from openvair.common.uow.base_sqlalchemy import BaseSqlAlchemyUnitOfWork
from openvair.modules.virtual_machines.config import DEFAULT_SESSION_FACTORY
from openvair.modules.virtual_machines.adapters import repository

if TYPE_CHECKING:
    from sqlalchemy.orm import sessionmaker


class VMSqlAlchemyUnitOfWork(BaseSqlAlchemyUnitOfWork):
    """SQLAlchemy-based implementation of the unit of work pattern.

    This class provides an implementation of the unit of work pattern using
    SQLAlchemy for managing database transactions. It ensures that a series
    of operations on the virtual machines repository are performed within
    a single transaction.

    Attributes:
        session_factory (sessionmaker): The SQLAlchemy session factory.
    """

    def __init__(self, session_factory: sessionmaker = DEFAULT_SESSION_FACTORY):
        """Initialize the SqlAlchemyUnitOfWork with a session factory.

        Args:
            session_factory (sessionmaker): The SQLAlchemy session factory.
        """
        super().__init__(session_factory)

    def _init_repositories(self) -> None:
        """Initializes repositories for the virtual machines module."""
        self.virtual_machines = repository.VMSqlAlchemyRepository(
            self.session
        )
