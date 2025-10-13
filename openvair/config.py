"""Configuration settings and utility functions for the OpenVair project.

This module handles the loading of configuration from a TOML file and provides
utility functions to generate PostgreSQL database URIs and SQLAlchemy session
factories.

Constants:
    PROJECT_ROOT (Path): Root directory of the project.
    toml_path (Path): Path to the TOML configuration file.

Functions:
    get_postgres_uri() -> str: Generates a PostgreSQL URI from configuration
        settings.
    get_default_session_factory() -> sessionmaker: creates and returns a
        SQLAlchemy session factory with the given parameters.
"""

import pathlib
import tempfile

import toml
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from openvair.rpc_queues import RPCQueueNames
from openvair.abstracts.exceptions import ConfigParameterNotSpecifiedError

PROJECT_ROOT = pathlib.Path(__file__).parent.parent
TMP_DIR = tempfile.gettempdir()

# Path to the TOML configuration file
toml_path = pathlib.Path(__file__).parent.parent / 'project_config.toml'

RPC_QUEUES: type[RPCQueueNames] = RPCQueueNames

with pathlib.Path.open(toml_path, 'r') as config_toml:
    data = toml.load(config_toml)

database: dict = data.get('database', {})
DB_CONTAINER: str = data['docker']['db_container']


def get_postgres_uri() -> str:
    """Generates a PostgreSQL URI from configuration settings.

    Returns:
        str: PostgreSQL URI for connecting to the database.
    """
    try:
        port: int = database['port']
        host: str = database['host']
        password: str = database['password']
        user: str = database['user']
        db_name: str = database['db_name']
    except KeyError as err:
        msg = f'{err} - for database section'
        raise ConfigParameterNotSpecifiedError(msg)
    return f'postgresql://{user}:{password}@{host}:{port}/{db_name}'


def get_default_session_factory(
    pool_size: int = 10,
    max_overflow: int = 10,
    pool_timeout: int = 60,
    pool_recycle: int = 1800,  # refresh connections every 30 minutes
    *,
    pool_pre_ping: bool = True,
) -> sessionmaker:
    """Creates and returns SQLAlchemy session factory with the given parameters.

    Args:
        pool_size (int): The size of the connection pool.
        max_overflow (int): The maximum number of connections to allow
            beyond pool_size.
        pool_timeout (int): The number of seconds to wait before giving up
            on acquiring a connection.
        pool_recycle (int): The number of seconds after which to recycle
            connections.
        pool_pre_ping (bool): Whether to check connections before using them.

    Returns:
        sessionmaker: A SQLAlchemy session factory.
    """
    return sessionmaker(
        expire_on_commit=False,
        bind=create_engine(
            get_postgres_uri(),
            isolation_level='REPEATABLE READ',
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_timeout=pool_timeout,
            pool_pre_ping=pool_pre_ping,
            pool_recycle=pool_recycle,
        ),
    )
