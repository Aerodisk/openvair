"""Custom exceptions for the network domain layer.

This module defines custom exceptions used in the network domain layer
for handling errors related to network interface and bridge operations.

Classes:
    BridgeAllreadyExistOnNetplanConfigError: Raised when bridge name exist in
        current netplan config.
    PortNetplanFileNotFoundError: Raised when file with port name config not
        found
    NoYAMLContentFoundFromNetplanGetError: Raised when not found network yaml
        info in 'netplan get'
    ErrorYamlParsinError: Raised when getting error while parsing yaml string
"""

from typing import Any

from openvair.abstracts.base_exception import BaseCustomException


class NetplanFileNotFoundException(BaseCustomException):
    """Raised when file with port name config not found"""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize NetplanFileNotFoundException"""
        super().__init__(message, *args)


class NoYAMLContentFoundFromNetplanGetError(BaseCustomException):
    """Raised when not found network yaml info in 'netplan get'"""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize NoYAMLContentFoundFromNetplanGetError"""
        super().__init__(message, *args)


class YamlParsinError(BaseCustomException):
    """Raised when getting error while parsing yaml string"""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize ErrorYamlParsinError"""
        super().__init__(message, *args)


class NetplanConfigReadingException(BaseCustomException):
    """Raised when 'netplan get' cannot read configurations"""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize NetplanConfigReadingException"""
        super().__init__(message, *args)
