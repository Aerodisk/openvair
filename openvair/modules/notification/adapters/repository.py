"""Repository pattern implementation for notifications.

This module implements the repository pattern to manage Notification entities
in the database using SQLAlchemy.
"""

from typing import TYPE_CHECKING, cast

from openvair.modules.notification.adapters.orm import Notification
from openvair.common.repositories.base_sqlalchemy import (
    BaseSqlAlchemyRepository,
)

if TYPE_CHECKING:
    from sqlalchemy.orm import Session
    from sqlalchemy.orm.mapper import Mapper


class NotificationSqlAlchemyRepository(BaseSqlAlchemyRepository[Notification]):
    """SQLAlchemy-based implementation of the notification repository."""

    def __init__(self, session: 'Session'):
        """Repository for managing Notification entities.

        Args:
            session (Session): The SQLAlchemy session to use for database
                operations.
        """
        super().__init__(session, Notification)

    def _get_notifications_by_type(
        self, notifications_type: str
    ) -> Notification | None:
        """Retrieve notifications by their type.

        Args:
            notifications_type (str): The type of notifications to retrieve.

        Returns:
            Optional[Notification]: A list of notifications of the specified
            type or None.
        """
        return (
            self.session.query(Notification)
            .filter_by(name=notifications_type)
            .first()
        )

    def _get_notifications_by_subject(
        self, notification_subject: str
    ) -> Notification | None:
        """Retrieve notifications by their subject.

        Args:
            notification_subject (str): The subject of notifications to
                retrieve.

        Returns:
            Optional[Notification]: A list of notifications with the specified
                subject or None.
        """
        return (
            self.session.query(Notification)
            .filter_by(name=notification_subject)
            .first()
        )

    def _bulk_update(self, data: list[dict]) -> None:
        """Perform a bulk update on notifications.

        Args:
            data (List[Dict]): A list of dictionaries containing the updated
                notification data.
        """
        self.session.bulk_update_mappings(cast('Mapper', Notification), data)
