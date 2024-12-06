"""Repository pattern implementation for notifications.

This module defines abstract and concrete repositories for managing
notifications in the database. It includes functionality for adding, retrieving,
updating, and deleting notifications.
"""

import abc
from uuid import UUID
from typing import TYPE_CHECKING, Dict, List, Optional, cast

from sqlalchemy.exc import OperationalError
from sqlalchemy.orm.mapper import Mapper

from openvair.abstracts.exceptions import DBCannotBeConnectedError
from openvair.modules.notification.adapters.orm import Notification

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class AbstractRepository(metaclass=abc.ABCMeta):
    """Abstract base class for notification repositories."""

    def _check_connection(self) -> None:
        """Check the database connection.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError

    def add(self, notification: Notification) -> None:
        """Add a notification to the repository.

        Args:
            notification (Notification): The notification to add.
        """
        self._add(notification)

    def get(self, notification_id: UUID) -> Notification:
        """Retrieve a notification by its ID.

        Args:
            notification_id (UUID): The ID of the notification to retrieve.

        Returns:
            Notification: The retrieved notification.
        """
        return self._get(notification_id)

    def get_all(self) -> List[Notification]:
        """Retrieve all notifications.

        Returns:
            List[Notification]: A list of all notifications.
        """
        return self._get_all()

    def get_notifications_by_type(
        self, notifications_type: str
    ) -> Optional[Notification]:
        """Retrieve notifications by their type.

        Args:
            notifications_type (str): The type of notifications to retrieve.

        Returns:
            List[Notification]: A list of notifications of the specified type.
        """
        return self._get_notifications_by_type(notifications_type)

    def get_notifications_by_subject(
        self, notifications_subject: str
    ) -> Optional[Notification]:
        """Retrieve notifications by their subject.

        Args:
            notifications_subject (str): The subject of notifications to
                retrieve.

        Returns:
            List[Notification]: A list of notifications with the specified
                subject.
        """
        return self._get_notifications_by_subject(notifications_subject)

    def delete(self, notification_id: UUID) -> None:
        """Delete a notification by its ID.

        Args:
            notification_id (UUID): The ID of the notification to delete.
        """
        return self._delete(notification_id)

    def bulk_update(self, data: List[Dict]) -> None:
        """Perform a bulk update on notifications.

        Args:
            data (List[Dict]): A list of dictionaries containing the updated
                notification data.
        """
        self._bulk_update(data)

    @abc.abstractmethod
    def _add(self, notification: Notification) -> None:
        """Add a notification to the repository.

        Args:
            notification (Notification): The notification to add.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _get(self, notification_id: UUID) -> Notification:
        """Retrieve a notification by its ID.

        Args:
            notification_id (UUID): The ID of the notification to retrieve.

        Returns:
            Notification: The retrieved notification.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _get_all(self) -> List[Notification]:
        """Retrieve all notifications.

        Returns:
            List[Notification]: A list of all notifications.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _get_notifications_by_type(
        self, notifications_type: str
    ) -> Optional[Notification]:
        """Retrieve notifications by their type.

        Args:
            notifications_type (str): The type of notifications to retrieve.

        Returns:
            List[Notification]: A list of notifications of the specified type.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _get_notifications_by_subject(
        self, notification_subject: str
    ) -> Optional[Notification]:
        """Retrieve notifications by their subject.

        Args:
            notification_subject (str): The subject of notifications to
                retrieve.

        Returns:
            List[Notification]: A list of notifications with the specified
                subject.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _delete(self, notification_id: UUID) -> None:
        """Delete a notification by its ID.

        Args:
            notification_id (UUID): The ID of the notification to delete.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _bulk_update(self, data: List[Dict]) -> None:
        """Perform a bulk update on notifications.

        Args:
            data (List[Dict]): A list of dictionaries containing the updated
                notification data.
        """
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    """SQLAlchemy-based implementation of the notification repository."""

    def __init__(self, session: 'Session'):
        """Initialize the SqlAlchemyRepository.

        Args:
            session (Session): The SQLAlchemy session to use for database
                operations.
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

    def _add(self, notification: Notification) -> None:
        """Add a notification to the repository.

        Args:
            notification (Notification): The notification to add.
        """
        self.session.add(notification)

    def _get(self, notification_id: UUID) -> Notification:
        """Retrieve a notification by its ID.

        Args:
            notification_id (UUID): The ID of the notification to retrieve.

        Returns:
            Notification: The retrieved notification.
        """
        return (
            self.session.query(Notification).filter_by(id=notification_id).one()
        )

    def _get_all(self) -> List[Notification]:
        """Retrieve all notifications.

        Returns:
            List[Notification]: A list of all notifications.
        """
        return self.session.query(Notification).all()

    def _get_notifications_by_type(
        self, notifications_type: str
    ) -> Optional[Notification]:
        """Retrieve notifications by their type.

        Args:
            notifications_type (str): The type of notifications to retrieve.

        Returns:
            List[Notification]: A list of notifications of the specified type.
        """
        return (
            self.session.query(Notification)
            .filter_by(name=notifications_type)
            .first()
        )

    def _get_notifications_by_subject(
        self, notification_subject: str
    ) -> Optional[Notification]:
        """Retrieve notifications by their subject.

        Args:
            notification_subject (str): The subject of notifications to
                retrieve.

        Returns:
            List[Notification]: A list of notifications with the specified
                subject.
        """
        return (
            self.session.query(Notification)
            .filter_by(name=notification_subject)
            .first()
        )

    def _delete(self, notification_id: UUID) -> None:
        """Delete a notification by its ID.

        Args:
            notification_id (UUID): The ID of the notification to delete.
        """
        self.session.query(Notification).filter_by(id=notification_id).delete()

    def _bulk_update(self, data: List[Dict]) -> None:
        """Perform a bulk update on notifications.

        Args:
            data (List[Dict]): A list of dictionaries containing the updated
                notification data.
        """
        self.session.bulk_update_mappings(cast(Mapper, Notification), data)
