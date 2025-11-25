"""Service-layer specific exceptions for scheduler module."""

from openvair.modules.scheduler.shared.base_exceptions import (
    BaseSchedulerServiceLayerException,
)


class JobNotFoundError(BaseSchedulerServiceLayerException):
    """Raised when a scheduler job with the given ID or name cannot be found."""

    pass


class JobInvalidNameError(BaseSchedulerServiceLayerException):
    """Raised when the job name is empty, too short or otherwise invalid."""

    pass


class JobInvalidCronExpression(BaseSchedulerServiceLayerException):
    """Raised when the cron expression is syntactically incorrect or unsafe."""

    pass


class JobNameAlreadyExists(BaseSchedulerServiceLayerException):
    """Raised when creating or renaming a job to a name that already exists."""

    pass


class JobFieldIsNotEditable(BaseSchedulerServiceLayerException):
    """Raised when editing a job's attribute when it is not editable."""

    pass


### RabbitMQ


class MessageDoesNotHaveAction(BaseSchedulerServiceLayerException):
    """Raised when 'action' field is missing in message."""

    pass
