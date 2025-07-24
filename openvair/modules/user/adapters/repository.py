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
    SqlAlchemyRepository._get_all: Retrieves a list of users from the database.
    SqlAlchemyRepository._delete: Deletes a user by ID from the database.
"""

from typing import TYPE_CHECKING

from openvair.modules.user.adapters.orm import User
from openvair.common.repositories.base_sqlalchemy import (
    BaseSqlAlchemyRepository,
)

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

class SqlAlchemyRepository(BaseSqlAlchemyRepository[User]):
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
        _get_all: Retrieves a list of users from the database.
        _delete: Deletes a user by ID from the database.
    """

    def __init__(self, session: 'Session'):
        """Initialize the SqlAlchemyRepository with a session.

        Args:
            session (Session): The SQLAlchemy session to use.
        """
        super().__init__(session, User)

    def get_by_name(self, username: str) -> User:
        """Retrieve a user by username from the database.

        Args:
            username (str): The username of the user to retrieve.

        Returns:
            User: The user entity with the specified username.
        """
        return self.session.query(User).filter_by(username=username).one()
