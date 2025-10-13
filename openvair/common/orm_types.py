"""Common ORM types used across the application.

This module defines custom SQLAlchemy types to handle conversion between
Python types and database-compatible types. In particular, it provides a type
to automatically convert pathlib.Path objects to strings and vice versa.
"""

from pathlib import Path

from sqlalchemy.types import String, TypeDecorator
from sqlalchemy.engine import Dialect  # тип для параметра dialect


class PathType(TypeDecorator):
    """A custom SQLAlchemy type for handling pathlib.Path objects.

    This type converts a pathlib.Path instance to its string representation when
    storing in the database, and converts a string back to a pathlib.Path when
    retrieving from the database.

    Attributes:
        impl (Type): The underlying database type (String).
    """

    impl = String

    def process_bind_param(
        self, value: Path | str | None, dialect: Dialect
    ) -> str | None:
        """Convert a Python value to a database-compatible value.

        This method is called before the value is sent to the database. If the
        value is a pathlib.Path instance, it is converted to a string.

        Args:
            value (Optional[Union[Path, str]]): The value to be bound to a SQL
                parameter. It can be a pathlib.Path, a string, or None.
            dialect (Dialect): The database dialect in use.

        Returns:
            Optional[str]: The string representation of the path if value is a
                Path,
            the original string if value is already a string, or None.
        """
        _ = dialect  # Warning suppression: the parameter is not used.
        if value is None:
            return value
        if isinstance(value, Path):
            return str(value)
        return value

    def process_result_value(
        self, value: str | None, dialect: Dialect
    ) -> Path | None:
        """Convert a database value to a Python value.

        This method is called after a value is retrieved from the database.
        It converts a string to a pathlib.Path object.

        Args:
            value (Optional[str]): The value retrieved from the database.
            dialect (Dialect): The database dialect in use.

        Returns:
            Optional[Path]: A pathlib.Path instance if the value is not None,
            otherwise None.
        """
        _ = dialect  # Warning suppression: the parameter is not used.
        if value is None:
            return value
        return Path(value)
