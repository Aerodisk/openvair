"""Module for providing abstract base classes for block device interfaces.

This module defines two abstract base classes: `BaseBlockInterface` and
`BaseFibreChannelInterface`. These classes provide a common interface for
interacting with different types of block device interfaces, such as ISCSI
and Fibre Channel.

Classes:
    BaseBlockInterface: Abstract base class for block device interfaces.
    BaseFibreChannelInterface: Abstract base class for Fibre Channel interfaces.
    BaseISCSI: Abstract base class for ISCSI interfaces.
    BaseFibreChannel: Abstract base class for Fibre Channel interfaces that
        inherits from `BaseFibreChannelInterface`.
"""

from __future__ import annotations

import abc
from typing import Any

from openvair.libs.log import get_logger

LOG = get_logger(__name__)


class BaseBlockInterface(metaclass=abc.ABCMeta):
    """Abstract base class for block device interfaces.

    This class provides a common interface for interacting with different types
    of block device interfaces, such as ISCSI and Fibre Channel.

    Attributes:
        ip (str): The IP address of the block device interface.
        inf_type (str): The type of the block device interface.
        port (str): The port number of the block device interface.
    """

    def __init__(self, **kwargs: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize a BaseBlockInterface object.

        Args:
            **kwargs:
                ip (str, optional): The IP address of the block device
                    interface. Defaults to an empty string.
                inf_type (str, optional): The type of the block device
                    interface. Defaults to an empty string.
                port (int, optional): The port number of the block device
                    interface.
                    Defaults to '3260'.
        """
        self.ip = kwargs.get('ip', '')
        self.inf_type = kwargs.get('inf_type', '')
        self.port = kwargs.get('port') or '3260'

    @abc.abstractmethod
    def discovery(self) -> str:
        """Discover the block device interface.

        Returns:
            str: The result of the discovery operation.
        """
        ...

    @abc.abstractmethod
    def get_host_iqn(self) -> str:
        """Get the host IQN (ISCSI Qualified Name).

        Returns:
            str: The host IQN.
        """
        ...

    @abc.abstractmethod
    def login(self) -> dict:
        """Log in to the block device interface.

        Returns:
            Dict: The result of the login operation.
        """
        ...

    @abc.abstractmethod
    def logout(self) -> dict:
        """Log out of the block device interface.

        Returns:
            Dict: The result of the logout operation.
        """
        ...


class BaseFibreChannelInterface(metaclass=abc.ABCMeta):
    """Abstract base class for Fibre Channel interfaces.

    This class provides a common interface for interacting with Fibre Channel
    block device interfaces.
    """

    @abc.abstractmethod
    def lip_scan(self) -> str:
        """Perform a Loop Initialization Protocol (LIP) scan."""
        ...


class BaseISCSI(BaseBlockInterface):
    """Abstract base class for ISCSI interfaces.

    This class inherits from `BaseBlockInterface` and provides additional
    ISCSI-specific functionality.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize a BaseISCSI object.

        Args:
            *args: Positional arguments passed to the `BaseBlockInterface`
                constructor.
            **kwargs:
                ip (str, optional): The IP address of the block device
                    interface.
                    Defaults to an empty string.
                inf_type (str, optional): The type of the block device
                    interface.
                    Defaults to an empty string.
                port (int, optional): The port number of the block device
                    interface.
                    Defaults to '3260'.
        """
        super().__init__(*args, **kwargs)

    @abc.abstractmethod
    def get_host_iqn(self) -> str:
        """Get the host IQN (ISCSI Qualified Name).

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.

        Returns:
            str: The host IQN.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def discovery(self) -> str:
        """Discover the ISCSI interface.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.

        Returns:
            str: The result of the discovery operation.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def login(self) -> dict:
        """Log in to the block device interface.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.

        Returns:
            Dict: The result of the login operation.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def logout(self) -> dict:
        """Log out of the block device interface.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.

        Returns:
            Dict: The result of the logout operation.
        """
        raise NotImplementedError


class BaseFibreChannel(BaseFibreChannelInterface):
    """Abstract base class for FIBRE channels.

    his class inherits from `BaseFibreChannelInterface` and provides additional
    Fibre channel functionality.
    """

    @abc.abstractmethod
    def lip_scan(self) -> str:
        """Perform a Loop Initialization Protocol (LIP) scan."""
        raise NotImplementedError
