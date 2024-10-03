"""Base classes for notifications.

This module provides the `BaseNotification` and `BaseEmailNotification` classes,
which serve as abstract base classes for various types of notifications.
"""

import abc
import uuid

from openvair.libs.log import get_logger

LOG = get_logger(__name__)


class BaseNotification(metaclass=abc.ABCMeta):
    """Abstract base class for notifications."""

    def __init__(self, **kwargs):
        """Initialize a `BaseNotification` instance.

        Args:
            **kwargs: Arbitrary keyword arguments, which may include:
                - id (str): The unique identifier for the notification.
                - send_datetime (datetime): The time the notification was sent.
                - message (str): The content of the notification.
                - recipients (List): The list of recipients for the
                    notification.
                - msg_type (str): The type of message.
        """
        self.id = str(kwargs.get('id', uuid.uuid4()))
        self.send_datetime = kwargs.get('send_datetime', None)
        self.message = kwargs.get('message', '')
        self.recipients = kwargs.get('recipients')
        self.params_for_type = kwargs.get(kwargs.get('msg_type', ''), {})
        LOG.info('Initialized BaseNotification')

    @abc.abstractmethod
    def send(self) -> None:
        """Send the notification.

        This method must be implemented by subclasses to define how the
        notification is sent.
        """
        ...


class BaseEmailNotification(BaseNotification):
    """Abstract base class for email notifications."""

    def __init__(self, *args, **kwargs):
        """Initialize a `BaseEmailNotification` instance.

        Args:
           *args: Variable length argument list.
           **kwargs: Arbitrary keyword arguments, which may include:
                - smtp_server (str): The SMTP server to use for sending emails.
                - smtp_port (int): The port to use for the SMTP server.
                - smtp_username (str): The username for the SMTP server.
                - smtp_password (str): The password for the SMTP server.
        """
        super().__init__(*args, **kwargs)
        self.smtp_server = self.params_for_type.get('smtp_server')
        self.smtp_port = self.params_for_type.get('smtp_port')
        self.smtp_username = self.params_for_type.get('smtp_username')
        self.smtp_password = self.params_for_type.get('smtp_password')
        LOG.info('Initialized BaseEmailNotification')

    def send(self) -> None:
        """Send the email notification.

        This method must be implemented by subclasses to define how the
        email notification is sent.
        """
        raise NotImplementedError
