"""Repository module for managing PostgreSQL databases.

This module defines an abstract base class for database repositories and
provides a concrete implementation using SQLAlchemy to manage PostgreSQL
databases. It includes methods for terminating connections, dropping databases,
creating databases
"""

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING

from sqlalchemy import text, create_engine

from openvair.config import database, get_postgres_uri

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class AbstractRepository(metaclass=ABCMeta):
    """Abstract base class for database repositories.

    Defines the interface for database operations such as terminating
    connections, dropping databases, creating databases, and restoring data.
    """

    @abstractmethod
    def terminate_all_connections(self, db_name: str) -> None:
        """Terminate all active connections to a specified database.

        Args:
            db_name (str): Name of the database whose connections should be
                terminated.
        """
        ...

    @abstractmethod
    def drop_db(self, db_name: str) -> None:
        """Drop a specified database.

        Args:
            db_name (str): Name of the database to drop.
        """
        ...

    @abstractmethod
    def create_db(self, db_name: str) -> None:
        """Create a new database.

        Args:
            db_name (str): Name of the database to create.
        """
        ...


class SqlAlchemyRepository(AbstractRepository):
    """SQLAlchemy implementation of a database repository.

    This class provides concrete implementations of database operations
    using SQLAlchemy, tailored for PostgreSQL.

    Attributes:
        session (Session): SQLAlchemy session for database interactions.
        engine (Engine): SQLAlchemy engine for executing database commands.
    """
    def __init__(self, session: 'Session'):
        """Initialize the SQLAlchemy repository.

        Args:
            session (Session): SQLAlchemy session for database interactions.
        """
        self.session: Session = session
        self.engine = create_engine(
            get_postgres_uri().replace(
                database['db_name'], 'postgres'
            )  # for connection to 'postgres' db, instead 'openvair'
        )

    def terminate_all_connections(self, db_name: str) -> None:
        """Terminate all active connections to a specified database.

        Uses a SQL query to terminate all connections to the specified database,
        except the current session.

        Args:
            db_name (str): Name of the database whose connections should be
                terminated.
        """
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
        """Drop a specified database.

        Executes a SQL command to drop the database. All connections to the
        database are terminated before the drop operation.

        Args:
            db_name (str): Name of the database to drop.
        """
        with self.engine.connect().execution_options(
            isolation_level='AUTOCOMMIT'
        ) as conn:  # connect withot transaction
            # Stop all connections
            conn.execute(
                text("""
                    SELECT pg_terminate_backend(pg_stat_activity.pid)
                    FROM pg_stat_activity
                    WHERE pg_stat_activity.datname = :db_name
                    AND pid <> pg_backend_pid();
                """),
                {'db_name': db_name},
            )

            conn.execute(text(f'DROP DATABASE "{db_name}";'))

    def create_db(self, db_name: str) -> None:
        """Create a new database.

        Executes a SQL command to create a new database.

        Args:
            db_name (str): Name of the database to create.
        """
        with self.engine.connect().execution_options(
            isolation_level='AUTOCOMMIT'
        ) as conn:  # Connect without transaction
            conn.execute(text(f'CREATE DATABASE "{db_name}";'))

