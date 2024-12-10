"""Module for custom exceptions in the backup domain.

Classes:
    BackupDomainException: base exception class for exceptions in backup domain
"""

from openvair.abstracts.base_exception import BaseCustomException


class BackupDomainException(BaseCustomException):
    """Base exception class for exceptions in backup domain"""
    ...
