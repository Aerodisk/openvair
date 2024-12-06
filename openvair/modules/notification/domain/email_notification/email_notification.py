"""Module for handling email notifications.

This module provides the `EmailNotification` class, which is responsible for
sending email notifications using SMTP.
"""

import smtplib
from typing import Any
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from openvair.libs.log import get_logger
from openvair.modules.notification.domain.base import BaseEmailNotification
from openvair.modules.notification.domain.exceptions import (
    NotificationSMTPException,
    NoRecipientsSpecifiedForEmailNotification,
)

LOG = get_logger(__name__)


class EmailNotification(BaseEmailNotification):
    """Class representing an email notification."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize an `EmailNotification` instance.

        Args:
            args: Variable length argument list.
            kwargs: Arbitrary keyword arguments, which may include:
                - subject (str): The subject of the email.
        """
        super().__init__(*args, **kwargs)
        self.subject = str(kwargs.get('subject', ''))
        LOG.info('Initialized EmailNotification')

    def send(self) -> None:
        """Send the email notification.

        This method triggers the sending of the email to all recipients.
        """
        return self._send()

    def _send(self) -> None:
        """Send the email notification to all specified recipients.

        Raises:
            NoRecipientsSpecifiedForEmailNotification: If no recipients are
                specified for the email.
        """
        if not self.recipients:
            raise NoRecipientsSpecifiedForEmailNotification(
                str(self.recipients)
            )

        for recipient in self.recipients:
            self._send_msg_to_recipient(recipient)

    def _send_msg_to_recipient(self, recipient: str) -> None:
        """Send the email notification to a single recipient.

        Args:
            recipient (str): The recipient's email address.
        """
        LOG.info('Sending message to recipient: %s ...', recipient)
        msg = self._construct_msg()
        msg['To'] = recipient
        complete_msg = msg.as_string()

        server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
        try:
            server.login(self.smtp_username, self.smtp_password)
            server.sendmail(self.smtp_username, recipient, complete_msg)
            server.close()
            LOG.info('Message was sent to recipient: %s', recipient)
        except smtplib.SMTPException as err:
            error = NotificationSMTPException(str(err))
            LOG.error(str(error))
            raise error

    def _construct_msg(self) -> MIMEMultipart:
        """Construct the email message to be sent.

        Returns:
            MIMEMultipart: The constructed email message.
        """
        msg = MIMEMultipart()
        msg['From'] = self.smtp_username
        msg['Subject'] = self.subject
        msg.attach(MIMEText(self.message, 'plain'))
        return msg
