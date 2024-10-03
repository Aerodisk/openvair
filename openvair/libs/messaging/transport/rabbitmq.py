"""RabbitMQ connection module.

This module provides a base class for establishing a connection to a RabbitMQ
server using the `pika` library.

Classes:
    BaseRabbitMQConnection: Base class for creating a transport connection to
        RabbitMQ using the `pika` library.
"""

import pika

from openvair.libs.messaging import config


class BaseRabbitMQConnection:
    """Base class for creating a RabbitMQ transport connection using `pika`.

    This class sets up the connection parameters and establishes a connection
    to the RabbitMQ server.

    Attributes:
        params (pika.URLParameters): Connection parameters for the RabbitMQ URL.
        connection (pika.BlockingConnection): The established blocking
            connection to RabbitMQ.
        channel (pika.channel.Channel): The channel for communication with
            RabbitMQ.
    """

    # Create connection parameters from the RabbitMQ URL
    params = pika.URLParameters(config.get_rabbitmq_url())

    def __init__(self):
        """Initialize the RabbitMQ connection and channel."""
        self.params.blocked_connection_timeout = 10
        self.connection = pika.BlockingConnection(self.params)
        self.channel = self.connection.channel()
