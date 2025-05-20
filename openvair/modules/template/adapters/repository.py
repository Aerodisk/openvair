"""SQLAlchemy repository for the template module.

This module provides a repository implementation for managing templates using
SQLAlchemy.

Classes:
    - TemplateSqlAlchemyRepository: Repository for template entities.
"""

from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from openvair.modules.template.adapters.orm import Template
from openvair.common.repositories.base_sqlalchemy import (
    BaseSqlAlchemyRepository,
)
from openvair.modules.template.adapters.exceptions import (
    TemplateNotFoundException,
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
        """Retrieves a template by its unique name.

        Uses the SQLAlchemy one() method to ensure that the result is strictly
        a Template.

        Returns:
            Template: The matching template entity.

        Raises:
            TemplateNotFoundException: If no template with the given name is
                found.
        """
        try:
            return self.session.query(self.model_cls).filter_by(name=name).one()
        except NoResultFound as e:
            message = f"Template with name '{name}' not found."
            raise TemplateNotFoundException(message) from e
