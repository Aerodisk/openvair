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

from openvair.modules.tools.base_exception import BaseCustomException


class RpcCallException(BaseCustomException):
    """Exception raised when an RPC call fails."""

    def __init__(self, *args):
        """Initialize the RpcCallException."""
        super().__init__(*args)


class RpcCallTimeoutException(BaseCustomException):
    """Exception raised when an RPC call times out."""

    def __init__(self):
        """Initialize the RpcCallTimeoutException."""
        self.message = 'Timed out waiting for a response'
        super().__init__(self.message)


class RpcClientInitializedException(BaseCustomException):
    """Exception raised during RPC client initialization."""

    def __init__(self):
        """Initialize the RpcClientInitializedException."""
        self.message = 'An error occurred during client initialization'
        super().__init__(self.message)


class RpcServerInitializedException(BaseCustomException):
    """Exception raised during RPC server initialization."""

    def __init__(self):
        """Initialize the RpcServerInitializedException."""
        self.message = 'An error occurred during server initialization'
        super().__init__(self.message)
