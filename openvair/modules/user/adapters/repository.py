"""Repository layer for user management.

This module defines the abstract and concrete repository implementations
for managing user entities. It includes methods for adding, retrieving,
and deleting users from the database.

Classes:
    AbstractRepository: Abstract base class for user repository operations.
    SqlAlchemyRepository: Concrete implementation of AbstractRepository
        using SQLAlchemy for database operations.

Exceptions:
    DBCannotBeConnectedError: Custom exception raised when the database
        connection fails.

Methods:
    AbstractRepository._check_connection: Abstract method for checking
        database connection.
    SqlAlchemyRepository._check_connection: Checks the database connection
        and raises an exception if the connection fails.
    SqlAlchemyRepository._add: Adds a user to the database.
    SqlAlchemyRepository._get: Retrieves a user by ID from the database.
    SqlAlchemyRepository._get_by_name: Retrieves a user by username from
        the database.
    SqlAlchemyRepository._delete: Deletes a user by ID from the database.
"""

import abc
from typing import TYPE_CHECKING

from sqlalchemy.exc import OperationalError

from openvair.modules.user.adapters.orm import User
from openvair.modules.user.adapters.exceptions import DBCannotBeConnectedError

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class AbstractRepository(metaclass=abc.ABCMeta):
    """Abstract base class for user repository operations.

    This class defines the interface for managing user entities in the
    repository. It includes abstract methods for adding, retrieving, and
    deleting users.

    Methods:
        _check_connection: Abstract method to check the database connection.
        add: Adds a user to the repository.
        get: Retrieves a user by ID from the repository.
        get_by_name: Retrieves a user by username from the repository.
        delete: Deletes a user by ID from the repository.
    """
    def _check_connection(self) -> None:
        """Check the database connection.

        This method must be implemented in subclasses to ensure that the
        repository is properly connected to the database.
        """
        raise NotImplementedError

    # User operation

    def add(self, user: User) -> None:
        """Add a user to the repository.

        Args:
            user (User): The user entity to add.
        """
        self._add(user)

    def get(self, user_id: str) -> User:
        """Retrieve a user by ID from the repository.

        Args:
            user_id (str): The ID of the user to retrieve.

        Returns:
            User: The user entity with the specified ID.
        """
        return self._get(user_id)

    def get_by_name(self, username: str) -> User:
        """Retrieve a user by username from the repository.

        Args:
            username (str): The username of the user to retrieve.

        Returns:
            User: The user entity with the specified username.
        """
        return self._get_by_name(username)

    def delete(self, user_id: str) -> None:
        """Delete a user by ID from the repository.

        Args:
            user_id (str): The ID of the user to delete.
        """
        self._delete(user_id)

    @abc.abstractmethod
    def _add(self, user: User) -> None:
        """Add a user to the repository.

        Args:
            user (User): The user entity to add.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _get(self, user_id: str) -> User:
        """Retrieve a user by ID from the repository.

        Args:
            user_id (str): The ID of the user to retrieve.

        Returns:
            User: The user entity with the specified ID.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _get_by_name(self, username: str) -> User:
        """Retrieve a user by username from the repository.

        Args:
            username (str): The username of the user to retrieve.

        Returns:
            User: The user entity with the specified username.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _delete(self, user_id: str) -> None:
        """Delete a user by ID from the repository.

        Args:
            user_id (str): The ID of the user to delete.
        """
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    """Concrete implementation of AbstractRepository using SQLAlchemy.

    This class provides the actual implementation of repository methods
    using SQLAlchemy ORM for database operations.

    Args:
        session (Session): The SQLAlchemy session to use for database operations

    Methods:
        _check_connection: Checks the database connection and raises an
            exception if the connection fails.
        _add: Adds a user to the database.
        _get: Retrieves a user by ID from the database.
        _get_by_name: Retrieves a user by username from the database.
        _delete: Deletes a user by ID from the database.
    """

    def __init__(self, session: "Session"):
        """Initialize the SqlAlchemyRepository with a session.

        Args:
            session (Session): The SQLAlchemy session to use.
        """
        super().__init__()
        self.session: Session = session
        self._check_connection()

    def _check_connection(self) -> None:
        """Check the database connection.

        Raises:
            DBCannotBeConnectedError: If the database connection cannot be
                established.
        """
        try:
            self.session.connection()
        except OperationalError:
            raise DBCannotBeConnectedError(message="Can't connect to Database")

    def _add(self, user: User) -> None:
        """Add a user to the database.

        Args:
            user (User): The user entity to add.
        """
        self.session.add(user)

    def _get(self, user_id: str) -> User:
        """Retrieve a user by ID from the database.

        Args:
            user_id (str): The ID of the user to retrieve.

        Returns:
            User: The user entity with the specified ID.
        """
        return self.session.query(User).filter_by(id=user_id).one()

    def _get_by_name(self, username: str) -> User:
        """Retrieve a user by username from the database.

        Args:
            username (str): The username of the user to retrieve.

        Returns:
            User: The user entity with the specified username.
        """
        return self.session.query(User).filter_by(username=username).one()

    def _delete(self, user_id: str) -> None:
        """Delete a user by ID from the database.

        Args:
            user_id (str): The ID of the user to delete.
        """
        self.session.query(User).filter_by(id=user_id).delete()
