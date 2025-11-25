"""SQLAlchemy repository for the block_device module.

This module implements the repository pattern to manage ISCSIInterface entities
in the database using SQLAlchemy.
"""

from typing import TYPE_CHECKING

from openvair.modules.block_device.adapters.orm import ISCSIInterface
from openvair.common.repositories.base_sqlalchemy import (
    BaseSqlAlchemyRepository,
)

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

class BlockDeviceSqlAlchemyRepository(BaseSqlAlchemyRepository[ISCSIInterface]):
    """Repository for managing ISCSIInterface entities.

    This class provides CRUD operations for the block_device model using
    SQLAlchemy.
    """

    def __init__(self, session: 'Session'):
        """Initializes the repository with a database session.

        Args:
            session (Session): SQLAlchemy session for accessing the database
                tables
        """
        super().__init__(session, ISCSIInterface)

    def get_by_ip(self, interface_ip: str) -> ISCSIInterface:
        """Retrieve a ISCSIInterface by its ip.

        Args:
            interface_ip (str): The ip of the ISCSIInterface to fetch.

        Returns:
            ISCSIInterface: The ISCSIInterface instance from the database.
        """
        return (
            self.session.query(ISCSIInterface).filter_by(ip=interface_ip).one()
        )
