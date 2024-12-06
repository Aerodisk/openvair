"""_summary_"""

import abc
from typing import Dict, Type, Generic, TypeVar

T = TypeVar('T')


class AbstractDataSerializer(Generic[T], metaclass=abc.ABCMeta):
    """Abstract class for data serialization."""

    @classmethod
    @abc.abstractmethod
    def to_domain(
        cls,
        orm_object: T,
    ) -> Dict:
        """Convert an ORM object to a domain dictionary."""
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def to_db(
        cls,
        data: Dict,
        orm_class: Type[T],
    ) -> T:
        """Convert a dictionary to an ORM object."""
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def to_web(
        cls,
        orm_object: T,
    ) -> Dict:
        """Convert an ORM object to a web dictionary."""
        raise NotImplementedError
