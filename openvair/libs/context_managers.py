"""Context managers for working with database sessions and file system changes.

This module provides two main context managers:

1. synchronized_session: Creates a nested transaction within the current
    SQLAlchemy session, handling commits and rollbacks in case of errors.

2. change_directory: Temporarily changes the current working directory,
    restoring the original directory upon exit from the context.
"""

import os
from typing import (
    TYPE_CHECKING,
    Any,
    Generator,
)
from pathlib import Path
from contextlib import contextmanager

from sqlalchemy.exc import OperationalError

from openvair.libs.log import get_logger

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

LOG = get_logger(__name__)


@contextmanager
def synchronized_session(session: 'Session') -> Generator:
    """Creates a context for safely executing database session operations.

    This context manager creates a nested transaction within the current
    transaction of the given SQLAlchemy session. It ensures that changes
    are committed if successful, or rolled back in case of an error.

    Args:
        session (sqlalchemy.orm.Session): The SQLAlchemy session to execute
            operations on.

    Yields:
        sqlalchemy.orm.Session: The SQLAlchemy session within the
            synchronization context.

    Raises:
        OperationalError: Any operational error from the database engine
            will trigger a rollback before propagating the exception.
    """
    try:
        yield session.begin_nested()
        session.commit()
    except OperationalError:
        session.rollback()
        raise


@contextmanager
def change_directory(destination: Path) -> Generator[None, Any, None]:
    """Temporarily changes the current working directory.

    This context manager switches the working directory to the specified
    destination for the duration of the context. After exiting the context,
    it restores the original working directory.

    Args:
        destination (Path): The directory to change to during the context.

    Yields:
        None: No values are yielded; the context simply changes the directory.

    Example:
        with change_directory(Path('/tmp')):
            # Current working directory is now "/tmp".
            ...
        # Original working directory is restored.
    """
    original_directory = Path.cwd()
    try:
        os.chdir(destination)
        yield
    finally:
        os.chdir(original_directory)
