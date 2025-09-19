"""_summary_"""

import abc
from typing import Generic, TypeVar

from sqlalchemy.orm import DeclarativeBase

T = TypeVar('T', bound=DeclarativeBase)


class AbstractDataSerializer(Generic[T], metaclass=abc.ABCMeta):
    """Abstract class for data serialization."""

    @classmethod
    @abc.abstractmethod
    def to_domain(
        cls,
        orm_object: T,
    ) -> dict:
        """Convert an ORM object to a domain dictionary."""
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def to_db(
        cls,
        data: dict,
        orm_class: type[T],
    ) -> T:
        """Convert a dictionary to an ORM object."""
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def to_web(
        cls,
        orm_object: T,
    ) -> dict:
        """Convert an ORM object to a web dictionary."""
        raise NotImplementedError
