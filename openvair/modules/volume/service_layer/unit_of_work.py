"""Module for handling unit of work in the volume service layer.

This module defines the abstract and concrete implementations of the Unit
of Work pattern for managing database transactions in the volume service
layer. It ensures that operations on the database are performed within a
transactional context, allowing for rollback in case of errors.

Classes:
    AbstractUnitOfWork: Abstract base class for unit of work.
    SqlAlchemyUnitOfWork: Concrete implementation of the unit of work using
        SQLAlchemy.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from openvair.modules.volume.config import DEFAULT_SESSION_FACTORY
from openvair.modules.volume.adapters import repository
from openvair.common.uow.base_sqlalchemy import BaseSqlAlchemyUnitOfWork

if TYPE_CHECKING:
    from sqlalchemy.orm import sessionmaker


class VolumeSqlAlchemyUnitOfWork(BaseSqlAlchemyUnitOfWork):
    """Concrete implementation of unit of work using SQLAlchemy.

    This class provides a SQLAlchemy-based implementation of the Unit of
    Work pattern, managing the transaction boundaries for operations on
    volume-related entities.

    Attributes:
    volumes (VolumeSqlAlchemyRepository): Repository for volume entities.
    """

    def __init__(self, session_factory: sessionmaker = DEFAULT_SESSION_FACTORY):
        """Initialize the Unit of Work with a session factory.

        Args:
            session_factory (callable, optional): A factory function that
                returns a SQLAlchemy session.
                Defaults to `DEFAULT_SESSION_FACTORY`.
        """
        super().__init__(session_factory)

    def _init_repositories(self) -> None:
        """Initializes repositories for the volume module."""
        self.volumes = repository.VolumeSqlAlchemyRepository(self.session)
