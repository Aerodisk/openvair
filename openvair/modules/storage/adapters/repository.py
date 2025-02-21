"""Module for storage repository patterns using SQLAlchemy.

This module defines abstract and SQLAlchemy-based repository patterns for
interacting with storage-related data in the database.

Classes:
    AbstractRepository: Abstract base class defining the storage repository
        interface.
    SqlAlchemyRepository: SQLAlchemy implementation of the storage repository
        interface.
"""

import abc
from uuid import UUID
from typing import TYPE_CHECKING, Any, List, Union, Optional, cast

from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.mapper import Mapper

from openvair.abstracts.exceptions import DBCannotBeConnectedError
from openvair.modules.storage.adapters.orm import Storage, StorageExtraSpecs

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class AbstractRepository(metaclass=abc.ABCMeta):
    """Abstract base class defining the storage repository interface.

    This class provides the interface for interacting with storage-related
    data in the database. It includes methods for adding, retrieving, updating,
    and deleting storage records, as well as filtering storage extra specs.
    """

    def _check_connection(self) -> None:
        """Check the database connection.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError

    def add(self, storage: Storage) -> None:
        """Add a new storage record.

        Args:
            storage (Storage): The storage record to add.
        """
        self._add(storage)

    def get(self, storage_id: UUID) -> Storage:
        """Retrieve a storage record by its ID.

        Args:
            storage_id (UUID): The ID of the storage to retrieve.

        Returns:
            Storage: The retrieved storage record.
        """
        return self._get(storage_id)

    def get_all(self) -> List[Storage]:
        """Retrieve all storage records.

        Returns:
            List[Storage]: A list of all storage records.
        """
        return self._get_all()

    def get_storage_by_name(self, storage_name: str) -> Optional[Storage]:
        """Retrieve a storage record by its name.

        Args:
            storage_name (str): The name of the storage to retrieve.

        Returns:
            Storage: The retrieved storage record.
        """
        return self._get_storage_by_name(storage_name)

    def delete(self, storage_id: UUID) -> None:
        """Delete a storage record by its ID.

        Args:
            storage_id (UUID): The ID of the storage to delete.
        """
        return self._delete(storage_id)

    def bulk_update(self, data: List) -> None:
        """Update multiple storage records in bulk.

        Args:
            data (List): A list of storage records to update.
        """
        self._bulk_update(data)

    @abc.abstractmethod
    def _add(self, storage: Storage) -> None:
        """Add a new storage record.

        Args:
            storage (Storage): The storage record to add.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _get(self, storage_id: UUID) -> Storage:
        """Retrieve a storage record by its ID.

        Args:
            storage_id (UUID): The ID of the storage to retrieve.

        Returns:
            Storage: The retrieved storage record.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _get_all(self) -> List[Storage]:
        """Retrieve all storage records.

        Returns:
            List[Storage]: A list of all storage records.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _get_storage_by_name(self, storage_name: str) -> Optional[Storage]:
        """Retrieve a storage record by its name.

        Args:
            storage_name (str): The name of the storage to retrieve.

        Returns:
            Storage: The retrieved storage record.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _delete(self, storage_id: UUID) -> None:
        """Delete a storage record by its ID.

        Args:
            storage_id (UUID): The ID of the storage to delete.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _bulk_update(self, data: List) -> None:
        """Update multiple storage records in bulk.

        Args:
            data (List): A list of storage records to update.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError

    # StorageExtraSpecs methods

    def filter_extra_specs(
        self,
        *,
        all_rows: bool = True,
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
        return self._filter_extra_specs(all_rows=all_rows, **kwargs)

    def get_spec_by_key_value(
        self, key: str, value: str
    ) -> Optional[StorageExtraSpecs]:
        """Retrieve a storage extra spec by key and value.

        Args:
            key (str): The key of the extra spec.
            value (str): The value of the extra spec.

        Returns:
            StorageExtraSpecs: The retrieved storage extra spec.
        """
        return self._get_spec_by_key_value(key, value)

    def update_spec_by_key_for_storage(
        self, key: str, value: str, storage_id: UUID
    ) -> None:
        """Update a storage extra spec by key for a specific storage.

        Args:
            key (str): The key of the extra spec to update.
            value (str): The new value for the extra spec.
            storage_id (UUID): The ID of the storage to update.
        """
        self._update_spec_by_key_for_storage(key, value, storage_id)

    @abc.abstractmethod
    def _filter_extra_specs(
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

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _get_spec_by_key_value(
        self, key: str, value: str
    ) -> Optional[StorageExtraSpecs]:
        """Retrieve a storage extra spec by key and value.

        Args:
            key (str): The key of the extra spec.
            value (str): The value of the extra spec.

        Returns:
            StorageExtraSpecs: The retrieved storage extra spec.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _update_spec_by_key_for_storage(
        self, key: str, value: str, storage_id: UUID
    ) -> None:
        """Update a storage extra spec by key for a specific storage.

        Args:
            key (str): The key of the extra spec to update.
            value (str): The new value for the extra spec.
            storage_id (UUID): The ID of the storage to update.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
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
        super(SqlAlchemyRepository, self).__init__()
        self.session: Session = session
        self._check_connection()

    def _check_connection(self) -> None:
        """Check the database connection.

        Raises:
            DBCannotBeConnectedError: If a connection to the database cannot
                be established.
        """
        try:
            self.session.connection()
        except OperationalError:
            raise DBCannotBeConnectedError(message="Can't connect to Database")

    def _add(self, storage: Storage) -> None:
        """Add a new storage record.

        Args:
            storage (Storage): The storage record to add.
        """
        self.session.add(storage)

    def _get(self, storage_id: UUID) -> Storage:
        """Retrieve a storage record by its ID.

        Args:
            storage_id (UUID): The ID of the storage to retrieve.

        Returns:
            Storage: The retrieved storage record.
        """
        return (
            self.session.query(Storage)
            .options(joinedload(Storage.extra_specs))
            .filter_by(id=storage_id)
            .one()
        )

    def _get_all(self) -> List[Storage]:
        """Retrieve all storage records.

        Returns:
            List[Storage]: A list of all storage records.
        """
        return (
            self.session.query(Storage)
            .options(joinedload(Storage.extra_specs))
            .all()
        )

    def _get_storage_by_name(self, storage_name: str) -> Optional[Storage]:
        """Retrieve a storage record by its name.

        Args:
            storage_name (str): The name of the storage to retrieve.

        Returns:
            Storage: The retrieved storage record.
        """
        return self.session.query(Storage).filter_by(name=storage_name).first()

    def _delete(self, storage_id: UUID) -> None:
        """Delete a storage record by its ID.

        Args:
            storage_id (str): The ID of the storage to delete.
        """
        (
            self.session.query(StorageExtraSpecs)
            .filter_by(storage_id=storage_id)
            .delete(synchronize_session=False)
        )
        self.session.query(Storage).filter_by(id=storage_id).delete()

    def _filter_extra_specs(
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

    def _get_spec_by_key_value(
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

    def _update_spec_by_key_for_storage(
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

    def _bulk_update(self, data: List) -> None:
        """Update multiple storage records in bulk.

        Args:
            data (List): A list of storage records to update.
        """
        self.session.bulk_update_mappings(cast(Mapper, Storage), data)
