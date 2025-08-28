"""Unit of Work implementation for the block_device module.

This module defines a SQLAlchemy-based Unit of Work for managing
interface-related transactions and repositories.

Classes:
    BlockDeviceSqlAlchemyUnitOfWork: Unit of Work for the block_device module.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from openvair.common.uow.base_sqlalchemy import BaseSqlAlchemyUnitOfWork
from openvair.modules.block_device.config import DEFAULT_SESSION_FACTORY
from openvair.modules.block_device.adapters import repository

if TYPE_CHECKING:
    from sqlalchemy.orm import sessionmaker


class BlockDeviceSqlAlchemyUnitOfWork(BaseSqlAlchemyUnitOfWork):
    """Unit of Work for the block_device module.

    This class manages database transactions for interfaces, ensuring
    consistency by committing or rolling back operations.

    Attributes:
        interfaces (BlockDeviceSqlAlchemyRepository): Repository for
            ISCSIInterface entities.
    """

    def __init__(self, session_factory: sessionmaker = DEFAULT_SESSION_FACTORY):
        """Initializes the Unit of Work with a session factory.

        Args:
            session_factory (sessionmaker): SQLAlchemy session factory.
                Defaults to DEFAULT_SESSION_FACTORY.
        """
        super().__init__(session_factory)

    def _init_repositories(self) -> None:
        """Initializes repositories for the block_device module."""
        self.interfaces = repository.BlockDeviceSqlAlchemyRepository(
            self.session
        )
