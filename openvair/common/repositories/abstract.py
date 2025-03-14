"""Abstract repository base class.

This module defines an abstract repository interface that provides
common CRUD operations for working with data.

Classes:
    - AbstractRepository: Base repository interface with CRUD methods.
"""

import abc
from typing import List, Generic, TypeVar, Optional

T = TypeVar('T')


class AbstractRepository(abc.ABC, Generic[T]):
    """Abstract base repository with CRUD methods.

    This class provides a template for repositories handling data storage
    operations.
    """

    @abc.abstractmethod
    def add(self, entity: T) -> None:
        """Adds a new entity to the repository.

        Args:
            entity (T): The entity to add.
        """
        ...

    @abc.abstractmethod
    def get(self, entity_id: int) -> Optional[T]:
        """Retrieves an entity by its ID.

        Args:
            entity_id (int): The ID of the entity.

        Returns:
            Optional[T]: The retrieved entity or None if not found.
        """
        ...

    @abc.abstractmethod
    def get_all(self) -> List[T]:
        """Retrieves all entities from the repository.

        Returns:
            List[T]: A list of all stored entities.
        """
        ...

    @abc.abstractmethod
    def delete(self, entity_id: int) -> None:
        """Deletes an entity by its ID.

        Args:
            entity_id (int): The ID of the entity to delete.
        """
        ...

    @abc.abstractmethod
    def update(self, entity: T) -> None:
        """Updates an existing entity in the repository.

        Args:
            entity (T): The entity with updated data.
        """
        ...
