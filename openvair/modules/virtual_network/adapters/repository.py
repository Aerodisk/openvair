"""Repository pattern for the virtual network adapter.

This module provides abstract and concrete repository classes for managing
virtual networks and their port groups.

Classes:
    - AbstractRepository: Abstract base class for virtual network repository.
    - SqlAlchemyRepository: SQLAlchemy-based implementation of the virtual
        network repository.
"""

import abc
from uuid import UUID
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import joinedload

from openvair.abstracts.exceptions import DBCannotBeConnectedError
from openvair.modules.virtual_network.adapters.orm import (
    PortGroup,
    VirtualNetwork,
)

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class AbstractRepository(metaclass=abc.ABCMeta):
    """Abstract base class for virtual network repository."""

    @abc.abstractmethod
    def _check_connection(self) -> None:
        """Check the database connection.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError

    def get(self, virt_net_id: UUID) -> VirtualNetwork:
        """Get a virtual network by ID.

        Args:
            virt_net_id (UUID): The ID of the virtual network.

        Returns:
            VirtualNetwork: The virtual network object.
        """
        return self._get(virt_net_id)

    def get_by_name(self, virt_net_name: str) -> Optional[VirtualNetwork]:
        """Get a virtual network by name.

        Args:
            virt_net_name (str): The name of the virtual network.

        Returns:
            VirtualNetwork: The virtual network object.
        """
        return self._get_by_name(virt_net_name)

    def get_all(self) -> List:
        """Get all virtual networks.

        Returns:
            List: A list of all virtual network objects.
        """
        return self._get_all()

    def add(self, virtual_network: VirtualNetwork) -> None:
        """Add a virtual network.

        Args:
            virtual_network (VirtualNetwork): The virtual network to add.
        """
        self._add(virtual_network)

    def delete(self, vn_id: UUID) -> None:
        """Delete a virtual network by ID.

        Args:
            vn_id (UUID): The ID of the virtual network to delete.
        """
        return self._delete(vn_id)

    @abc.abstractmethod
    def _get(self, vn_id: UUID) -> VirtualNetwork:
        raise NotImplementedError

    @abc.abstractmethod
    def _get_by_name(self, vn_name: str) -> Optional[VirtualNetwork]:
        raise NotImplementedError

    @abc.abstractmethod
    def _get_all(self) -> List:
        raise NotImplementedError

    @abc.abstractmethod
    def _add(self, virtual_network: VirtualNetwork) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def _delete(self, vn_id: UUID) -> None:
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    """SQLAlchemy-based implementation of the virtual network repository."""

    def __init__(self, session: 'Session'):
        """Initialize the SqlAlchemyRepository.

        Args:
            session (Session): The SQLAlchemy session to use.
        """
        super(SqlAlchemyRepository, self).__init__()
        self.session = session
        self._check_connection()

    def _check_connection(self) -> None:
        """Check the database connection.

        Raises:
            DBCannotBeConnectedError: If the connection cannot be established.
        """
        try:
            self.session.connection()
        except OperationalError:
            raise DBCannotBeConnectedError(message="Can't connect to Database")

    def _get(self, vn_id: UUID) -> VirtualNetwork:
        """Get a virtual network by ID.

        Args:
            vn_id (str): The ID of the virtual network.

        Returns:
            VirtualNetwork: The virtual network object.
        """
        return (
            self.session.query(VirtualNetwork)
            .options(joinedload(VirtualNetwork.port_groups))
            .filter_by(id=vn_id)
            .one()
        )

    def _get_by_name(self, vn_name: str) -> Optional[VirtualNetwork]:
        """Get a virtual network by name.

        Args:
            vn_name (str): The name of the virtual network.

        Returns:
            VirtualNetwork: The virtual network object.
        """
        return (
            self.session.query(VirtualNetwork)
            .options(joinedload(VirtualNetwork.port_groups))
            .filter_by(network_name=vn_name)
            .first()
        )

    def _get_all(self) -> List:
        """Get all virtual networks.

        Returns:
            List: A list of all virtual network objects.
        """
        return (
            self.session.query(VirtualNetwork)
            .options(joinedload(VirtualNetwork.port_groups))
            .all()
        )

    def _add(self, virtual_network: VirtualNetwork) -> None:
        """Add a virtual network.

        Args:
            virtual_network (VirtualNetwork): The virtual network to add.
        """
        self.session.add(virtual_network)

    def _delete(self, vn_id: UUID) -> None:
        """Delete a virtual network by ID.

        Args:
            vn_id (UUID): The ID of the virtual network to delete.
        """
        self.session.query(PortGroup).filter_by(
            virtual_network_id=vn_id
        ).delete()
        self.session.query(VirtualNetwork).filter_by(id=vn_id).delete()
