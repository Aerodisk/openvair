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

import abc
from uuid import UUID
from typing import TYPE_CHECKING, List

from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import joinedload

from openvair.abstracts.exceptions import DBCannotBeConnectedError
from openvair.modules.network.adapters.orm import Interface, InterfaceExtraSpec

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class AbstractRepository(metaclass=abc.ABCMeta):
    """Abstract base class for the network interface repository.

    This class defines the interface for interacting with network interface
    data in the repository. Subclasses must provide implementations for all
    abstract methods.
    """

    def _check_connection(self) -> None:
        """Check the database connection.

        Raises:
            NotImplementedError: This method should be implemented by
                subclasses.
        """
        raise NotImplementedError

    # Interface

    def add(self, interface: Interface) -> None:
        """Add a new network interface to the repository.

        Args:
            interface (Interface): The network interface entity to add.
        """
        self._add(interface)

    def get(self, interface_id: UUID) -> Interface:
        """Retrieve a network interface by its ID.

        Args:
            interface_id (UUID): The unique identifier of the interface.

        Returns:
            Interface: The network interface entity matching the given ID.
        """
        return self._get(interface_id)

    def get_by_name(self, interface_name: str) -> Interface:
        """Retrieve a network interface by its name.

        Args:
            interface_name (str): The name of the interface to retrieve.

        Returns:
            Interface: The network interface entity matching the given name.
        """
        return self._get_by_name(interface_name)

    def get_all(self) -> List[Interface]:
        """Retrieve all network interfaces from the repository.

        Returns:
            List: A list of all network interfaces in the repository.
        """
        return self._get_all()

    def delete(self, interface_id: UUID) -> None:
        """Delete a network interface by its ID.

        Args:
            interface_id (UUID): The unique identifier of the interface to
                delete.
        """
        self._delete(interface_id)

    @abc.abstractmethod
    def _add(self, interface: Interface) -> None:
        """Add a new network interface to the repository.

        Args:
            interface (Interface): The network interface entity to add.

        Raises:
            NotImplementedError: This method should be implemented by
                subclasses.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _get(self, interface_id: UUID) -> Interface:
        """Retrieve a network interface by its ID.

        Args:
            interface_id (UUID): The unique identifier of the interface.

        Returns:
            Interface: The network interface entity matching the given ID.

        Raises:
            NotImplementedError: This method should be implemented by
                subclasses.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _get_by_name(self, interface_name: str) -> Interface:
        """Retrieve a network interface by its name.

        Args:
            interface_name (str): The name of the interface to retrieve.

        Returns:
            Interface: The network interface entity matching the given name.

        Raises:
            NotImplementedError: This method should be implemented by
                subclasses.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _get_all(self) -> List:
        """Retrieve all network interfaces from the repository.

        Returns:
            List: A list of all network interfaces in the repository.

        Raises:
            NotImplementedError: This method should be implemented by
                subclasses.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _delete(self, interface_id: UUID) -> None:
        """Delete a network interface by its ID.

        Args:
            interface_id (UUID): The unique identifier of the interface to
                delete.

        Raises:
            NotImplementedError: This method should be implemented by
                subclasses.
        """
        raise NotImplementedError

    # InterfaceExtraSpec

    def delete_extra_specs(self, interface_id: UUID) -> None:
        """Delete all extra specifications for a given interface.

        Args:
            interface_id (UUID): The ID of the interface whose extra
                specifications are to be deleted.
        """
        self._delete_extra_specs(interface_id)

    @abc.abstractmethod
    def _delete_extra_specs(self, interface_id: UUID) -> None:
        """Delete all extra specifications for a given interface.

        Args:
            interface_id (UUID): The ID of the interface whose extra
                specifications are to be deleted.

        Raises:
            NotImplementedError: This method should be implemented by
                subclasses.
        """
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
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
        super(SqlAlchemyRepository, self).__init__()
        self.session: Session = session
        self._check_connection()

    def _check_connection(self) -> None:
        """Check the database connection.

        This method attempts to establish a connection to the database
        and raises a `DBCannotBeConnectedError` if the connection fails.

        Raises:
            DBCannotBeConnectedError: If the database connection cannot be
                established.
        """
        try:
            self.session.connection()
        except OperationalError:
            raise DBCannotBeConnectedError(message="Can't connect to Database")

    def _add(self, interface: Interface) -> None:
        """Add a new network interface to the repository.

        Args:
            interface (Interface): The network interface entity to add.
        """
        self.session.add(interface)

    def _get(self, interface_id: UUID) -> Interface:
        """Retrieve a network interface by its ID.

        Args:
            interface_id (UUID): The unique identifier of the interface.

        Returns:
            Interface: The network interface entity matching the given ID.
        """
        return (
            self.session.query(Interface)
            .options(joinedload(Interface.extra_specs))
            .filter_by(id=interface_id)
            .one()
        )

    def _get_by_name(self, interface_name: str) -> Interface:
        """Retrieve a network interface by its name.

        Args:
            interface_name (str): The name of the interface to retrieve.

        Returns:
            Interface: The network interface entity matching the given name.
        """
        return (
            self.session.query(Interface)
            .options(joinedload(Interface.extra_specs))
            .filter_by(name=interface_name)
            .one()
        )

    def _get_all(self) -> List[Interface]:
        """Retrieve all network interfaces from the repository.

        Returns:
            List[Interface]: A list of all network interfaces in the repository.
        """
        return (
            self.session.query(Interface)
            .options(joinedload(Interface.extra_specs))
            .all()
        )

    def _delete(self, interface_id: UUID) -> None:
        """Delete a network interface by its ID.

        Args:
            interface_id (UUID): The unique identifier of the interface to
                delete.
        """
        self.session.query(Interface).filter_by(id=interface_id).delete()

    def _delete_extra_specs(self, interface_id: UUID) -> None:
        """Delete all extra specifications for a given interface.

        Args:
            interface_id (UUID): The ID of the interface whose extra
                specifications are to be deleted.
        """
        self.session.query(InterfaceExtraSpec).filter_by(
            interface_id=interface_id
        ).delete()
