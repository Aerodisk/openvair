"""Custom exception classes for repository-level errors.

This module defines custom exceptions used in repository implementations,
typically to indicate issues such as missing entities in the data source.

Classes:
    - EntityNotFoundError: Raised when an entity with the specified identifier
        is not found in the repository.
"""

from openvair.abstracts.base_exception import BaseCustomException


class EntityNotFoundError(BaseCustomException):
    """Raised when an entity is not found in the repository.

    Typically used in repository methods like `get_or_fail` or `delete_or_fail`
    when an entity with the specified identifier does not exist.
    """
    ...
