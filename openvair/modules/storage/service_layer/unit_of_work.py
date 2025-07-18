"""Unit of Work pattern for storage service layer.

This module defines the Unit of Work (UoW) pattern, which manages database
transactions for storage operations. It ensures that all operations related
to a storage entity are completed successfully before committing the changes
to the database.

Classes:
    AbstractUnitOfWork: Abstract base class defining the Unit of Work interface.
    SqlAlchemyUnitOfWork: Concrete implementation of the Unit of Work using
        SQLAlchemy.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from openvair.modules.storage.config import DEFAULT_SESSION_FACTORY
from openvair.modules.storage.adapters import repository
from openvair.common.uow.base_sqlalchemy import BaseSqlAlchemyUnitOfWork

if TYPE_CHECKING:
    from sqlalchemy.orm import sessionmaker


class StorageSqlAlchemyUnitOfWork(BaseSqlAlchemyUnitOfWork):
    """Concrete implementation of the Unit of Work pattern using SQLAlchemy.

    This class manages database transactions for storage operations using
    SQLAlchemy. It ensures that all operations are either fully completed or
    fully rolled back in case of errors.

    Attributes:
        storages (StorageSqlAlchemyRepository): Repository for storage entities.
    """

    def __init__(self, session_factory: sessionmaker = DEFAULT_SESSION_FACTORY):
        """Initialize the Unit of Work with a session factory.

        Args:
            session_factory (sessionmaker): A factory for creating new
                SQLAlchemy sessions. Defaults to DEFAULT_SESSION_FACTORY.
        """
        super().__init__(session_factory)

    def _init_repositories(self) -> None:
        """Initializes repositories for the storage module."""
        self.storages = repository.StorageSqlAlchemyRepository(self.session)
