"""This module contains classes that implement the repository pattern.

It includes an abstract base class `AbstractRepository` which defines
the interface for managing ISCSIInterface objects, and a concrete implementation
`SqlAlchemyRepository` which provides methods for accessing and manipulating
these objects in a SQLAlchemy database.

Classes:
    AbstractRepository: Abstract base class for the repository pattern.
    SqlAlchemyRepository: Concrete implementation of AbstractRepository
        using SQLAlchemy.
"""

import abc
from typing import TYPE_CHECKING, List

from sqlalchemy.exc import OperationalError

from openvair.abstracts.exceptions import DBCannotBeConnectedError
from openvair.modules.block_device.adapters.orm import ISCSIInterface

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class AbstractRepository(metaclass=abc.ABCMeta):
    """Implements the abstract repository pattern"""

    def _check_connection(self) -> None:
        """Check if the database is connected

        Raises:
            NotImplementedError: if the method called for abstract class
                instance
        """
        raise NotImplementedError

    # ISCSIInterface
    def add(self, interface: ISCSIInterface) -> None:
        """Abstract public method to add a new ISCSI interface

        Args:
            interface (ISCSIInterface): orm object of the ISCSCI interface
        """
        self._add(interface)

    def get(self, interface_id: str) -> ISCSIInterface:
        """Abstract public method to get an ISCSI interface by id

        Args:
            interface_id (str): database id of the ISCSCI interface

        Returns:
            ISCSIInterface: orm object of the ISCSI interface
        """
        return self._get(interface_id)

    def get_by_ip(self, interface_ip: str) -> ISCSIInterface:
        """Abstract public method to get an ISCSI interface by ip

        Args:
            interface_ip (str): ip address of the ISCSCI interface

        Returns:
            ISCSIInterface: orm object of the ISCSI interface
        """
        return self._get_by_ip(interface_ip)

    def get_all(self) -> List:
        """Abstract public method to get all ISCSI interfaces

        Returns:
            List: List of orm objects of the ISCSI interfaces
        """
        return self._get_all()

    def delete(self, interface_id: str) -> None:
        """Abstract public method to delete an ISCSI interface

        Args:
            interface_id (str): database ID of the ISCSI interface to delete
        """
        self._delete(interface_id)

    @abc.abstractmethod
    def _add(self, interface: ISCSIInterface) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def _get(self, interface_id: str) -> ISCSIInterface:
        raise NotImplementedError

    @abc.abstractmethod
    def _get_by_ip(self, interface_ip: str) -> ISCSIInterface:
        raise NotImplementedError

    @abc.abstractmethod
    def _get_all(self) -> List:
        raise NotImplementedError

    @abc.abstractmethod
    def _delete(self, interface_id: str) -> None:
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    """Implementation of the AbstractRepository for the block device module

    That class provides methods for accessing to database tables for
    manipulating data of the block device module.

    Args:
        AbstractRepository (_type_): _description_
    """

    def __init__(self, session: 'Session'):
        """Create a new instance of SqlAlchemyRepository

        Args:
            session (Session): SQLAlchemy session for accessing the database
                tables
        """
        super(SqlAlchemyRepository, self).__init__()
        self.session: 'Session' = session
        self._check_connection()

    def _check_connection(self) -> None:
        try:
            self.session.connection()
        except OperationalError:
            raise DBCannotBeConnectedError(message="Can't connect to Database")

    def _add(self, interface: ISCSIInterface) -> None:
        self.session.add(interface)

    def _get(self, interface_id: str) -> ISCSIInterface:
        return (
            self.session.query(ISCSIInterface).filter_by(id=interface_id).one()
        )

    def _get_by_ip(self, interface_ip: str) -> ISCSIInterface:
        return (
            self.session.query(ISCSIInterface).filter_by(ip=interface_ip).one()
        )

    def _get_all(self) -> List[ISCSIInterface]:
        return self.session.query(ISCSIInterface).all()

    def _delete(self, interface_id: str) -> None:
        return (
            self.session.query(ISCSIInterface)
            .filter_by(id=interface_id)
            .delete()
        )
