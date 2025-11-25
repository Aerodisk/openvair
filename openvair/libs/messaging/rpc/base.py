"""Base classes for RPC clients and servers.

This module contains basic classes (interfaces) to create specific
implementations of RPC entity classes

Classes:
    BaseRPCClient: Base class for implementing an RPC client.
    BaseRPCServer: Base class for implementing an RPC server.
"""

from abc import ABCMeta, abstractmethod
from typing import Any, Dict, Optional


class BaseRPCClient(metaclass=ABCMeta):
    """Base class for implementing an RPC client."""

    @abstractmethod
    def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: ANN401 # casue its base class
        """Initialize RPC Client"""
        pass

    @abstractmethod
    def on_response(self, *args: Any, **kwargs: Any) -> None:  # noqa: ANN401 # casue its base class
        """Handles incoming responses from the RPC server."""
        ...

    @abstractmethod
    def call(
        self,
        method_name: str,
        data_for_method: Optional[Dict] = None,
        data_for_manager: Optional[Dict] = None,
    ) -> Any:  # noqa: ANN401 TODO need to spicify response by pydantic
        """Sends a request to the RPC server and wait for a response."""
        ...

    @abstractmethod
    def cast(
        self,
        method_name: str,
        data_for_method: Optional[Dict] = None,
        data_for_manager: Optional[Dict] = None,
    ) -> None:
        """Sends a request to the RPC server without waiting for a response."""
        ...


class BaseRPCServer(metaclass=ABCMeta):
    """Base class for implementing an RPC server."""

    @abstractmethod
    def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: ANN401 # casue its base class
        """Initialize RPC Server"""
        pass

    @abstractmethod
    def on_request(self, *args: Any, **kwargs: Any) -> None:  # noqa: ANN401 # casue its base class
        """Handles incoming requests from the RPC client."""
        ...

    @abstractmethod
    def start(self) -> None:
        """Starts server instance"""
        ...
