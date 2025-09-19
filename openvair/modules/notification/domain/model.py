"""Factory and abstract classes for notifications.

This module provides the `AbstractNotificationFactory` and `NotificationFactory`
classes, which are responsible for creating notification objects based on the
input data.
"""

import abc
from typing import ClassVar, cast

from openvair.modules.notification.domain.base import BaseNotification
from openvair.modules.notification.domain.email_notification import (
    email_notification,
)


class AbstractNotificationFactory(metaclass=abc.ABCMeta):
    """Abstract base class for creating `BaseNotification` objects."""

    def __call__(self, db_notification: dict) -> BaseNotification:
        """Call the factory to get a notification object.

        Args:
            db_notification (Dict): Data dictionary representing the
                notification.

        Returns:
            BaseNotification: The created notification object.
        """
        return self.get_notification(db_notification)

    @abc.abstractmethod
    def get_notification(self, db_notification: dict) -> BaseNotification:
        """Create and return a notification object.

        Args:
            db_notification (Dict): Data dictionary representing the
                notification.

        Returns:
            BaseNotification: The created notification object.
        """
        ...


class NotificationFactory(AbstractNotificationFactory):
    """Factory for creating `Notification` objects based on type."""

    _notification_classes: ClassVar = {
        'email': email_notification.EmailNotification,
    }

    def get_notification(self, db_notification: dict) -> BaseNotification:
        """Create and return a notification object.

        Args:
            db_notification (Dict): Data dictionary representing the
                notification.

        Returns:
            BaseNotification: The created notification object.

        Raises:
            KeyError: If no matching notification class is found for the given
                notification type.
        """
        notification_class = self._notification_classes[
            db_notification['msg_type']
        ]
        return cast('BaseNotification', notification_class(**db_notification))
