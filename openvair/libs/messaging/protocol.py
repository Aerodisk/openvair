"""Messaging protocol module.

This module defines classes for selecting and initializing the appropriate
protocol for RPC clients and servers, based on the messaging type and transport.

Classes:
    BaseProtocol: Abstract base class for protocol selection.
    RPCClient: Class for selecting and initializing an RPC client protocol.
    RPCServer: Class for selecting and initializing an RPC server protocol.
    Protocol: Class for dynamically initializing an RPC client or server based
        on configuration.
"""

import abc
from typing import Dict, Type, Generic, TypeVar, cast

from openvair.libs.messaging import exceptions
from openvair.libs.messaging.rpc import RabbitRPCClient, RabbitRPCServer
from openvair.libs.messaging.config import get_messaging_type_and_transport

RPCType = TypeVar('RPCType', RabbitRPCClient, RabbitRPCServer)


class BaseProtocol(metaclass=abc.ABCMeta):
    """Abstract base class for protocol selection."""

    @staticmethod
    @abc.abstractmethod
    def get_protocol(transport: str) -> Type:
        """Get the appropriate protocol class based on the transport.

        Args:
            transport (str): The transport method (e.g., 'rabbitmq').

        Returns:
            Type: The protocol class.
        """
        ...


class RPCClient(BaseProtocol):
    """Class for selecting and initializing an RPC client protocol."""

    @staticmethod
    def get_protocol(transport: str) -> Type[RabbitRPCClient]:
        """Get the RPC client class based on the transport method.

        Args:
            transport (str): The transport method (e.g., 'rabbitmq').

        Returns:
            Type: The RPC client class.

        Raises:
            RpcServerInitializedException: If the server initialization fails.
        """
        rpc_client_classes: Dict[str, Type[RabbitRPCClient]] = {
            'rabbitmq': RabbitRPCClient,
        }
        try:
            return rpc_client_classes[transport]
        except KeyError as _:
            raise exceptions.RpcServerInitializedException


class RPCServer(BaseProtocol):
    """Class for selecting and initializing an RPC server protocol."""

    @staticmethod
    def get_protocol(transport: str) -> Type[RabbitRPCServer]:
        """Get the RPC server class based on the transport method.

        Args:
            transport (str): The transport method (e.g., 'rabbitmq').

        Returns:
            Type: The RPC server class.

        Raises:
            RpcClientInitializedException: If the client initialization fails.
        """
        rpc_server_classes: Dict[str, Type[RabbitRPCServer]] = {
            'rabbitmq': RabbitRPCServer,
        }
        try:
            return rpc_server_classes[transport]
        except KeyError as _:
            raise exceptions.RpcClientInitializedException


class Protocol(Generic[RPCType]):
    """Class for dynamically initializing an RPC client or server.

    This class selects and initializes the appropriate RPC client or server
    based on the messaging type and transport configuration.
    """

    def __init__(
        self,
        *,
        client: bool = False,
        server: bool = False,
    ):
        """Initialize the Protocol.

        Args:
            client (Optional[bool]): Indicates if the protocol should be
                initialized as an RPC client.
            server (Optional[bool]): Indicates if the protocol should be
                initialized as an RPC server.
        """
        self.client = client
        self.server = server
        self._check_arguments()

    def __call__(self, *args, **kwargs) -> RPCType:
        """Initialize and return the appropriate RPC client or server.

        Based on the configuration, this method dynamically selects the
        appropriate RPC client or server protocol and returns an instance.

        Args:
            *args: Arguments passed to the protocol class constructor.
            **kwargs: Keyword arguments passed to the protocol class
                constructor.

        Returns:
            An instance of the selected RPC client or server class.

        Raises:
            AttributeError: If the messaging type or role (client/server) is not
                supported.
        """
        messaging_type, transport = get_messaging_type_and_transport()
        self._check_message_type(messaging_type)

        if self.client:
            protocol_instance = RPCClient.get_protocol(transport)(
                *args, **kwargs
            )
        elif self.server:
            protocol_instance = RPCServer.get_protocol(transport)(
                *args, **kwargs
            )
        else:
            msg = 'Neither client nor server is selected'
            raise AttributeError(msg)

        return cast(RPCType, protocol_instance)

    def _check_arguments(self) -> None:
        if self.client and self.server:
            msg = 'The client and server are selected both'
            raise AttributeError(msg)

    @staticmethod
    def _check_message_type(messaging_type: str) -> None:
        if messaging_type != 'rpc':
            msg = 'Unsupported messaging type'
            raise AttributeError(msg)
