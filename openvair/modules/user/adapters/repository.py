"""SQLAlchemy repository for the user module.

This module implements the repository pattern to manage User entities
in the database using SQLAlchemy.

Classes:
    UserSqlAlchemyRepository: Class for database operations. Concrete
        implementation of BaseSqlAlchemyRepository.
"""

from typing import TYPE_CHECKING

from openvair.modules.user.adapters.orm import User
from openvair.common.repositories.base_sqlalchemy import (
    BaseSqlAlchemyRepository,
)

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

class UserSqlAlchemyRepository(BaseSqlAlchemyRepository[User]):
    """Repository for managing user entities.

    Args:
        session (Session): The SQLAlchemy session to use for database operations
    """

    def __init__(self, session: 'Session'):
        """Initialize the UserSqlAlchemyRepository with a session.

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
