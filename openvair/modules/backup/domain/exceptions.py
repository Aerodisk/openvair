"""Module for custom exceptions in the backup domain.

This module defines a hierarchy of custom exceptions for errors that may occur
during backup and restore operations, specifically for backuper logic.
"""

from openvair.abstracts.base_exception import BaseCustomException


class BaseBackuperError(BaseCustomException):
    """Base exception class for backup domain errors.

    This serves as the root exception for all Restic backuper-related errors
    in the backup domain.
    """

    ...


class BackupResticBackuperError(BaseBackuperError):
    """Raised for errors during backup operations."""

    ...


class RestoreResticBackuperError(BaseBackuperError):
    """Raised for errors during restore operations."""

    ...


class InitRepositoryResticBackuperError(BaseBackuperError):
    """Raised for errors initializing a repository."""

    ...


class SnapshotGettingResticBackuperError(BaseBackuperError):
    """Raised for errors during backup operations."""

    ...
