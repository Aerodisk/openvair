"""SQLAlchemy repository for the template module.

This module provides a repository implementation for managing templates using
SQLAlchemy.

Classes:
    - TemplateSqlAlchemyRepository: Repository for template entities.
"""

from sqlalchemy.orm import Session

from openvair.modules.template.adapters.orm import Template
from openvair.common.repositories.base_sqlalchemy import (
    BaseSqlAlchemyRepository,
)


class TemplateSqlAlchemyRepository(BaseSqlAlchemyRepository[Template]):
    """Repository for managing template entities.

    This class provides CRUD operations for the Template model using SQLAlchemy.
    """

    def __init__(self, session: Session) -> None:
        """Initializes the repository with a database session.

        Args:
            session (Session): The SQLAlchemy session for database operations.
        """
        super().__init__(session, Template)
