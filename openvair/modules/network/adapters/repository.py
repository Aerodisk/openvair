"""Repository pattern implementation for network module entities.

This module defines an abstract repository interface for managing network
interfaces and their extra specifications, along with a concrete implementation
using SQLAlchemy. The repository handles common CRUD operations and ensures
proper database connection handling.

Classes:
    AbstractRepository: Abstract base class defining the repository interface
        for network interface management.
    SqlAlchemyRepository: Concrete implementation of AbstractRepository using
        SQLAlchemy for database operations.
"""

from typing import TYPE_CHECKING, Optional

from openvair.modules.network.adapters.orm import Interface
from openvair.common.repositories.base_sqlalchemy import (
    BaseSqlAlchemyRepository,
)

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class NetworkSqlAlchemyRepository(BaseSqlAlchemyRepository[Interface]):
    """SQLAlchemy-based implementation of the network interface repository.

    This class provides concrete implementations of the methods defined in
    AbstractRepository for managing network interfaces and their extra
    specifications using SQLAlchemy.
    """

    def __init__(self, session: 'Session'):
        """Initialize the SqlAlchemyRepository with a database session.

        Args:
            session (Session): The SQLAlchemy session to use for database
                operations.
        """
        super().__init__(session, Interface)

    def get_by_name(self, interface_name: str) -> Optional[Interface]:
        """Retrieve a network interface by its name.

        Args:
            interface_name (str): The name of the interface to retrieve.

        Returns:
            Interface: The network interface entity matching the given name.
        """
        return (
            self.session.query(Interface).filter_by(name=interface_name).first()
        )
