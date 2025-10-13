"""RabbitMQ base classes module.

This module provides a base classes for creating concrete RabbitRPC entities.
Uses the `pika` library

Classes:
    BaseRabbitRPC: The base class for creating a BaseRabbitRPC client
        and server
    BaseRabbitRPCClient: The base class for creating concrete implementation of
        RabbitRPCClient.
    BaseRabbitRPCServer:The base class for creating concrete implementation of
        RabbitRPCServer.
"""

from abc import abstractmethod
from typing import Any
from collections.abc import Callable

import pika

from openvair.libs.messaging import config
from openvair.libs.messaging.rpc.base import BaseRPCClient, BaseRPCServer


class BaseRabbitRPC:
    """The base class for creating a Rabbit RPC client and server.

    This class initializes the connection, channel, and sets parameters for
    working with rabbitmq

    Attributes:
        params (pika.URLParameters): Connection parameters for the RabbitMQ URL.
        connection (pika.BlockingConnection): The established blocking
            connection to RabbitMQ.
        channel (pika.channel.Channel): The channel for communication with
            RabbitMQ.
    """

    params = pika.URLParameters(config.get_rabbitmq_url())

    def __init__(self) -> None:
        """Initialize the RabbitMQ connection and channel."""
        self.params.blocked_connection_timeout = 10.0  # type: ignore
        self.connection = pika.BlockingConnection(self.params)
        self.channel = self.connection.channel()


class BaseRabbitRPCClient(BaseRabbitRPC, BaseRPCClient):
    """The base class for creating concrete implementation of RabbitRPCClient.

    This class creates a callback queue for receiving responses from the
    RPC server.

    Attributes:
        callback_queue_name (str): Name of the callback queue.
        callback_queue (str): The declared callback queue.
        response (dict): Stores the server response.
        corr_id (str): Correlation ID for matching responses.
    """

    def __init__(self, queue_name: str, callback_queue_name: str = ''):
        """Initialize the RPC client with a callback queue.

        Args:
            queue_name (str): The name of the queue to send messages to.
            callback_queue_name (str): The name of the callback queue.
                Defaults to an empty string, which triggers automatic
                generation of a unique queue name.
        """
        self.queue_name = queue_name
        self.callback_queue_name = callback_queue_name
        super().__init__()
        result = self.channel.queue_declare(
            queue=self.callback_queue_name,
            exclusive=True,
            arguments={'x-max-priority': 10, 'x-max-length': 200},  # type: ignore
        )
        self.callback_queue = result.method.queue
        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True,
        )

        self.response: dict[str, dict] = {}
        self.corr_id: str | None = None

    @abstractmethod
    def on_response(
        self,
        channel: pika.adapters.blocking_connection.BlockingChannel,
        method: pika.spec.Basic.Deliver,
        props: pika.BasicProperties,
        body: bytes,
    ) -> None:
        """Handles incoming responses from the RPC server.

        This method deserializes the message body and stores the result in
        the `self.response` attribute.

        Args:
            channel: The channel on which the message was received.
            method: Delivery method.
            props: Message properties.
            body: The body of the message.
        """
        raise NotImplementedError

    @abstractmethod
    def call(
        self,
        method_name: str,
        data_for_method: dict | None = None,
        data_for_manager: dict | None = None,
        *,
        priority: int = 1,
        time_limit: int = 100,
    ) -> Any:  # noqa: ANN401 TODO need to spicify response by pydantic
        """Send a request to the RPC server and wait for a response.

        Args:
            method_name (str): The name of the method to be called on the
                server.
            data_for_method (Optional[Dict]): The data to be passed to the
                method.
            data_for_manager (Optional[Dict]): The data for initializing the
                manager.
            priority (int): The priority of the message. Defaults to 1.
            time_limit (int): The time limit for waiting for a response.
                Defaults to 100.

        Returns:
            Dict: The result of the method call on the RPC server.
        """
        raise NotImplementedError

    @abstractmethod
    def cast(
        self,
        method_name: str,
        data_for_method: dict | None = None,
        data_for_manager: dict | None = None,
        *,
        priority: int = 10,
    ) -> None:
        """Send a request to the RPC server without waiting for a response.

        Args:
            method_name (str): The name of the method to be called on the
                server.
            data_for_method (Optional[Dict]): The data to be passed to the
                method.
            data_for_manager (Optional[Dict]): The data for initializing the
                manager.
            priority (int): The priority of the message. Defaults to 10.
        """
        raise NotImplementedError


class BaseRabbitRPCServer(BaseRabbitRPC, BaseRPCServer):
    """The base class for creating concrete implementation of RabbitRPCServer.

    This class declares the queue for listening to incoming messages.
    """

    def __init__(self, queue_name: str, manager: Callable):
        """Initialize the RPC server with a specific queue.

        Args:
            queue_name (str): The name of the queue to listen to.
            manager: The manager class whose methods will be executed.
        """
        super().__init__()
        self.manager = manager
        self.channel.queue_declare(
            queue=queue_name,
            arguments={'x-max-priority': 10, 'x-max-length': 200},  # type: ignore
        )

    @abstractmethod
    def on_request(
        self,
        channel: pika.adapters.blocking_connection.BlockingChannel,
        method: pika.spec.Basic.Deliver,
        props: pika.BasicProperties,
        body: bytes,
    ) -> None:
        """Process incoming requests from the RPC client."""
        raise NotImplementedError

    @abstractmethod
    def start(self) -> None:
        """Start the server to listen for incoming messages."""
        raise NotImplementedError
