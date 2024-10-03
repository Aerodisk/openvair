"""Configuration settings for the user module.

This module contains configuration values for the user module, including
service layer queue names, JWT settings, and SQLAlchemy session factory.

Variables:
    USER_SERVICE_LAYER_QUEUE_NAME (str): The name of the queue for user
        service layer.
    JWT_SECRET (str): Secret key used for JWT encoding and decoding.
    TOKEN_TYPE (str): Type of token used in JWT (e.g., 'bearer').
    ALGORITHM (str): Algorithm used for encoding and decoding JWT.
    DEFAULT_SESSION_FACTORY (sessionmaker): SQLAlchemy session factory.
"""

from openvair import config
from openvair.config import RPC_QUEUES, get_default_session_factory

USER_SERVICE_LAYER_QUEUE_NAME: str  = RPC_QUEUES.User.SERVICE_LAYER

# JWT configuration settings
JWT_SECRET = config.data['jwt'].get('secret')
TOKEN_TYPE = config.data['jwt'].get('token_type')
ALGORITHM = config.data['jwt'].get('algorithm')

# Default SQLAlchemy session factory
DEFAULT_SESSION_FACTORY = get_default_session_factory()
