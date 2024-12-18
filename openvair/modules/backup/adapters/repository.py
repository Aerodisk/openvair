from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING

from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from openvair.abstracts.exceptions import DBCannotBeConnectedError

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class AbstractRepository(metaclass=ABCMeta):
    def __init__(self) -> None:
        self.session: Session

    def _check_connection(self) -> None:
        """Check the database connection.

        Raises:
            DBCannotBeConnectedError: If the connection cannot be established.
        """
        try:
            self.session.connection()
        except OperationalError:
            raise DBCannotBeConnectedError(message="Can't connect to Database")

    @abstractmethod
    def terminate_all_connections(self, db_name: str) -> None: ...

    @abstractmethod
    def drop_db(self, db_name: str) -> None: ...

    @abstractmethod
    def create_db(self, db_name: str) -> None: ...

    @abstractmethod
    def restore_data(self, db_name: str) -> None: ...


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session: 'Session'):
        self.session: Session = session
        self._check_connection()

    def terminate_all_connections(self, db_name: str) -> None:
        with self.session.connection() as conn:
            conn.execute(
                text("""
                        SELECT pg_terminate_backend(pg_stat_activity.pid)
                        FROM pg_stat_activity
                        WHERE pg_stat_activity.datname = :db_name
                        AND pid <> pg_backend_pid();
                    """),
                {'db_name': db_name},
            )

    def drop_db(self, db_name: str) -> None:
        with self.session.connection() as conn:
            conn.execute(text('DROP DATABASE :db_name;'), {'db_name': db_name})

    def create_db(self, db_name: str) -> None:
        with self.session.connection() as conn:
            conn.execute(
                text('CREATE DATABASE :db_name;'), {'db_name': db_name}
            )

    def restore_data(self, db_name: str) -> None:
        raise NotImplementedError
