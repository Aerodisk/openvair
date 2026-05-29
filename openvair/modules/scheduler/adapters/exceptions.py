"""Adapter-layer exceptions for the scheduler module.

This module defines exceptions related to scheduler operations at the adapter
level.

Classes:
    - SchedulerJobNotFoundException: Exception raised when a job is not found
        in the database.
"""

from openvair.abstracts.base_exception import BaseCustomException


class JobNotFoundInDBException(BaseCustomException):
    """Exception raised when a job is not found in the database."""
