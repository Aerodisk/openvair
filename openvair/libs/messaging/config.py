"""Messaging configuration module.

This module provides utility functions to retrieve RabbitMQ connection
parameters and messaging configuration details.

Functions:
    get_rabbitmq_url: Returns the RabbitMQ connection URL.
    get_messaging_type_and_transport: Retrieves the messaging type and transport
    method.
"""

from typing import Tuple

from openvair import config


def get_rabbitmq_url() -> str:
    """Get the RabbitMQ connection URL.

    This function constructs the RabbitMQ connection URL from configuration
    settings including the user, password, host, and port.

    Returns:
        str: The RabbitMQ connection URL.
    """
    rabbitmq = config.data.get('rabbitmq', {})
    user = rabbitmq.get('user', 'guest')
    password = rabbitmq.get('password', 'guest')
    host = rabbitmq.get('host', 'localhost')
    port = rabbitmq.get('port', 5672)
    return f'amqp://{user}:{password}@{host}:{port}'


def get_messaging_type_and_transport() -> Tuple[str, str]:
    """Get the messaging type and transport method.

    This function retrieves the messaging type and transport method from
    configuration settings.

    Returns:
        tuple: A tuple containing the messaging type and transport method.
    """
    messaging = config.data.get('messaging', {})
    return messaging.get('type', ''), messaging.get('transport', '')
