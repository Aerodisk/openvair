"""Messaging protocol module.

This module defines classes for selecting and initializing the appropriate
protocol for RPC clients and servers, based on the messaging type and transport.

Classes:
    BaseAgentMessagingFabric: Abstract base class for selecting messaging agent.
    ClientMessagingFabric: Class for selecting a client.
    ServerMessagingFabric: Class for selecting a server.
    MessagingClient: Class for creating and interacting with an RPC client.
    MessagingServer: Class for creating and running an RPC server.
"""

import abc
from typing import Any, Dict, Type, Callable, Optional

from openvair.libs.messaging import exceptions
from openvair.libs.messaging.config import get_messaging_type_and_transport
from openvair.libs.messaging.rpc.base import BaseRPCClient, BaseRPCServer
from openvair.libs.messaging.rpc.rabbit_rpc import (
    RabbitRPCClient,
    RabbitRPCServer,
)


class BaseAgentMessagingFabric(metaclass=abc.ABCMeta):
    """Abstract base class for selecting messaging agent."""

    @staticmethod
    @abc.abstractmethod
    def get_rpc_agent(transport: str) -> Type:
        """Get the appropriate protocol class based on the transport.

        Args:
            transport (str): The transport method (e.g., 'rabbitmq').

        Returns:
            Type: The protocol class.
        """
        ...


class ClientMessagingFabric(BaseAgentMessagingFabric):
    """Class for selecting a client."""

    @staticmethod
    def get_rpc_agent(transport: str) -> Type[BaseRPCClient]:
        """Get the client class based on the transport method.

        Args:
            transport (str): The transport method (e.g., 'rabbitmq').

        Returns:
            Type: The RPC client class.

        Raises:
            RpcServerInitializedException: If the server initialization fails.
        """
        rpc_client_classes: Dict[str, Type[BaseRPCClient]] = {
            'rabbitmq': RabbitRPCClient,
        }
        try:
            return rpc_client_classes[transport]
        except KeyError as err:
            raise exceptions.RpcServerInitializedException(str(err))


class ServerMessagingFabric(BaseAgentMessagingFabric):
    """Class for selecting a server."""

    @staticmethod
    def get_rpc_agent(transport: str) -> Type[BaseRPCServer]:
        """Get the server class based on the transport method.

        Args:
            transport (str): The transport method (e.g., 'rabbitmq').

        Returns:
            Type: The RPC server class.

        Raises:
            RpcClientInitializedException: If the client initialization fails.
        """
        rpc_server_classes: Dict[str, Type[BaseRPCServer]] = {
            'rabbitmq': RabbitRPCServer,
        }
        try:
            return rpc_server_classes[transport]
        except KeyError as err:
            raise exceptions.RpcClientInitializedException(str(err))


class MessagingServer:
    """Class for creating and running a server.

    This class initializes server based on the specified messaging
    type and transport, then provides a method to start the server.

    Attributes:
        queue_name (str): Name of the server's message queue.
        manager (Type): Manager class to handle server-side operations.
        server (BaseRPCServer): Instance of the server class.
    """

    messaging_type, transport = get_messaging_type_and_transport()

    def __init__(self, *, queue_name: str, manager: Callable) -> None:
        """Initialize the messaging server with the specified queue and manager.

        Args:
            queue_name (str): Name of the server's message queue.
            manager (Type): The manager class to handle operations on the
                server.

        Raises:
            AttributeError: If the messaging type is unsupported.
        """
        self.queue_name = queue_name
        self.manager = manager
        if self.messaging_type == 'rpc':
            server_class = ServerMessagingFabric.get_rpc_agent(self.transport)
            self.server = server_class(self.queue_name, self.manager)
        else:
            msg = f'Unsupported messaging type: {self.messaging_type}'
            raise AttributeError(msg)

    def start(self) -> None:
        """Start the server to listen for incoming messages."""
        self.server.start()


class MessagingClient:
    """Class for creating and interacting with client.

    This class initializes client based on the specified messaging
    type and transport, allowing method calls and asynchronous casts.

    Attributes:
        queue_name (str): Name of the client's message queue.
        callback_queue_name (str): Name of the client's callback queue for RPC
            responses.
        client (BaseRPCClient): Instance of the RPC client class.
    """

    messaging_type, transport = get_messaging_type_and_transport()

    def __init__(
        self,
        *,
        queue_name: str,
        callback_queue_name: str = '',
    ) -> None:
        """Initialize the messaging client with the specified queues.

        Args:
            queue_name (str): Name of the client's message queue.
            callback_queue_name (str): Optional name of the client's callback
                queue for responses.
        """
        self.queue_name = queue_name
        self.callback_queue_name = callback_queue_name
        if self.messaging_type == 'rpc':
            client_class = ClientMessagingFabric.get_rpc_agent(self.transport)
            self.client = client_class(
                self.queue_name,
                self.callback_queue_name,
            )

    def call(
        self,
        method_name: str,
        data_for_method: Optional[Dict] = None,
        data_for_manager: Optional[Dict] = None,
        **kwargs: Any,  # noqa: ANN401 if income spicific args like timout for Rabbit
    ) -> Any:  # noqa: ANN401 TODO need to spicify response by pydantic
        """Call a method on the RPC server and wait for a response.

        Args:
            method_name (str): Name of the method to call on the server.
            data_for_method (Optional[Dict]): Data to pass to the method.
            data_for_manager (Optional[Dict]): Additional data for the manager.
            **kwargs: Additional arguments for specific configurations
                (e.g., timeout).

        Returns:
            Any: Response from the server.
        """
        return self.client.call(
            method_name=method_name,
            data_for_method=data_for_method,
            data_for_manager=data_for_manager,
            **kwargs,
        )

    def cast(
        self,
        method_name: str,
        data_for_method: Optional[Dict] = None,
        data_for_manager: Optional[Dict] = None,
        **kwargs: Any,  # noqa: ANN401 if income spicific args like timout for Rabbit
    ) -> None:
        """Send a method to the RPC server without waiting for a response.

        Args:
            method_name (str): Name of the method to invoke on the server.
            data_for_method (Optional[Dict]): Data to pass to the method.
            data_for_manager (Optional[Dict]): Additional data for the manager.
            **kwargs: Additional arguments for specific configurations (e.g.,
                timeout).
        """
        self.client.cast(
            method_name=method_name,
            data_for_method=data_for_method,
            data_for_manager=data_for_manager,
            **kwargs,
        )
