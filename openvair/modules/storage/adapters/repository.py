"""Module for storage repository patterns using SQLAlchemy.

This module defines abstract and SQLAlchemy-based repository patterns for
interacting with storage-related data in the database.

Classes:
    AbstractRepository: Abstract base class defining the storage repository
        interface.
    SqlAlchemyRepository: SQLAlchemy implementation of the storage repository
        interface.
"""

from uuid import UUID
from typing import TYPE_CHECKING, Any, List, Union, Optional, cast

from openvair.modules.storage.adapters.orm import Storage, StorageExtraSpecs
from openvair.common.repositories.base_sqlalchemy import (
    BaseSqlAlchemyRepository,
)

if TYPE_CHECKING:
    from sqlalchemy.orm import Session
    from sqlalchemy.orm.mapper import Mapper


class StorageSqlAlchemyRepository(BaseSqlAlchemyRepository[Storage]):
    """SQLAlchemy implementation of the storage repository interface.

    This class provides methods for interacting with storage-related data
    in the database using SQLAlchemy. It includes methods for adding,
    retrieving, updating, and deleting storage records, as well as filtering
    storage extra specs.
    """

    def __init__(self, session: 'Session'):
        """Initialize SqlAlchemyRepository with a SQLAlchemy session.

        Args:
            session (Session): The SQLAlchemy session to use for database
                operations.
        """
        super().__init__(session, Storage)

    def get_storage_by_name(self, storage_name: str) -> Optional[Storage]:
        """Retrieve a storage record by its name.

        Args:
            storage_name (str): The name of the storage to retrieve.

        Returns:
            Storage: The retrieved storage record.
        """
        return self.session.query(Storage).filter_by(name=storage_name).first()

    def filter_extra_specs(
        self,
        *,
        all_rows: bool,
        **kwargs: Any,  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
    ) -> Union[Optional[StorageExtraSpecs], List[StorageExtraSpecs]]:
        """Filter storage extra specs based on criteria.

        Args:
            all_rows (bool): Whether to return all matching rows or just the
                first one.
            **kwargs: Additional filtering criteria.

        Returns:
            Union[StorageExtraSpecs, List[StorageExtraSpecs]]: The filtered
                storage extra specs.
        """
        if all_rows:
            return (
                self.session.query(StorageExtraSpecs).filter_by(**kwargs).all()
            )
        return self.session.query(StorageExtraSpecs).filter_by(**kwargs).first()

    def get_spec_by_key_value(
        self, key: str, value: str
    ) -> Optional[StorageExtraSpecs]:
        """Retrieve a storage extra spec by key and value.

        Args:
            key (str): The key of the extra spec.
            value (str): The value of the extra spec.

        Returns:
            Optional[StorageExtraSpecs]: The retrieved storage extra spec.
        """
        return (
            self.session.query(StorageExtraSpecs)
            .filter_by(key=key, value=value)
            .first()
        )

    def update_spec_by_key_for_storage(
        self, key: str, value: str, storage_id: UUID
    ) -> None:
        """Update a storage extra spec by key for a specific storage.

        Args:
            key (str): The key of the extra spec to update.
            value (str): The new value for the extra spec.
            storage_id (UUID): The ID of the storage to update.
        """
        (
            self.session.query(StorageExtraSpecs)
            .filter(
                StorageExtraSpecs.storage_id == storage_id,
                StorageExtraSpecs.key == key,
            )
            .update({'value': value})
        )

    def bulk_update(self, data: List) -> None:
        """Update multiple storage records in bulk.

        Args:
            data (List): A list of storage records to update.
        """
        self.session.bulk_update_mappings(cast('Mapper', Storage), data)
