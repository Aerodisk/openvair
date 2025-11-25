"""Repository pattern for the virtual network adapter.

This module provides abstract and concrete repository classes for managing
virtual networks and their port groups.

Classes:
    - AbstractRepository: Abstract base class for virtual network repository.
    - SqlAlchemyRepository: SQLAlchemy-based implementation of the virtual
        network repository.
"""

from typing import TYPE_CHECKING, Optional

from openvair.common.repositories.base_sqlalchemy import (
    BaseSqlAlchemyRepository,
)
from openvair.modules.virtual_network.adapters.orm import (
    VirtualNetwork,
)

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class VirtualNetworkSqlAlchemyRepository(
    BaseSqlAlchemyRepository[VirtualNetwork]
):
    """SQLAlchemy-based implementation of the virtual network repository."""

    def __init__(self, session: 'Session'):
        """Initialize the SqlAlchemyRepository.

        Args:
            session (Session): The SQLAlchemy session to use.
        """
        super().__init__(session, VirtualNetwork)

    def get_by_name(self, vn_name: str) -> Optional[VirtualNetwork]:
        """Get a virtual network by name.

        Args:
            vn_name (str): The name of the virtual network.

        Returns:
            VirtualNetwork: The virtual network object.
        """
        return (
            self.session.query(VirtualNetwork)
            .filter_by(network_name=vn_name)
            .first()
        )
