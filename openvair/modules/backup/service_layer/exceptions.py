"""Module for custom exceptions in the service layer of backup module.

Classes:
    BackupServiceLayerException: base exception class for exceptions in the
        service layer of backup module
"""

from openvair.abstracts.base_exception import BaseCustomException


class BackupServiceLayerException(BaseCustomException):
    """Base exception for exceptions in in the service layer of backup module"""

    ...


class WrongBackuperTypeError(BackupServiceLayerException):
    """Raised when getting wrong backuper type from config"""

    ...
