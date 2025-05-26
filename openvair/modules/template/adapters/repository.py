"""SQLAlchemy repository for the template module.

This module implements the repository pattern to manage Template entities
in the database using SQLAlchemy.
"""

from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from openvair.modules.template.adapters.orm import Template
from openvair.common.repositories.base_sqlalchemy import (
    BaseSqlAlchemyRepository,
)
from openvair.modules.template.adapters.exceptions import (
    TemplateNotFoundInDBException,
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

    def get_by_name(self, name: str) -> Template:
        """Retrieve a template by its unique name.

        Args:
            name (str): The unique name of the template to fetch.

        Returns:
            Template: The template instance from the database.

        Raises:
            TemplateNotFoundInDBException: If the template does not exist.
        """
        try:
            return self.session.query(self.model_cls).filter_by(name=name).one()
        except NoResultFound as e:
            message = f"Template with name '{name}' not found."
            raise TemplateNotFoundInDBException(message) from e
