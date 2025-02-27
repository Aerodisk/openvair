"""Custom exceptions for XML data handling.

This module defines custom exceptions used for handling errors related to
XML serialization and deserialization.

Classes:
    XMLSerializationError: Raised when an error occurs during XML serialization.
    XMLDeserializationError: Raised when an error occurs during XML
        deserialization.
"""

from openvair.abstracts.base_exception import BaseCustomException


class XMLSerializationError(BaseCustomException):
    """Exception raised for errors during XML serialization."""
    ...


class XMLDeserializationError(BaseCustomException):
    """Exception raised for errors during XML deserialization."""
    ...
