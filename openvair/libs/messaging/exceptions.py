"""Messaging exceptions module.

This module defines custom exceptions for handling errors in the messaging
system, particularly in the context of RPC communication.

Classes:
    RpcCallException: Exception raised when an RPC call fails.
    RpcCallTimeoutException: Exception raised when an RPC call times out.
    RpcClientInitializedException: Exception raised during RPC client
        initialization.
    RpcServerInitializedException: Exception raised during RPC server
        initialization.
"""

from typing import Any

from openvair.abstracts.base_exception import BaseCustomException


class RpcException(BaseCustomException):
    """Exception raised when an RPC call fails."""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize the RpcCallException."""
        super().__init__(message, *args)


class RpcCallException(RpcException):
    """Exception raised when an RPC call fails."""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize the RpcCallException."""
        super().__init__(message, *args)


class RpcCallTimeoutException(RpcException):
    """Exception raised when an RPC call times out."""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize the RpcCallTimeoutException."""
        self.message = 'Timed out waiting for a response'
        super().__init__(message, *args)


class RpcClientInitializedException(RpcException):
    """Exception raised during RPC client initialization."""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize the RpcClientInitializedException."""
        self.message = 'An error occurred during client initialization'
        super().__init__(message, *args)


class RpcServerInitializedException(RpcException):
    """Exception raised during RPC server initialization."""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize the RpcServerInitializedException."""
        self.message = 'An error occurred during server initialization'
        super().__init__(message, *args)


class RpcDeserializeMessageException(RpcException):
    """Exception raised when get error while parsing rpc message."""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize the RpcDeserializeMessageException."""
        super().__init__(message, *args)
