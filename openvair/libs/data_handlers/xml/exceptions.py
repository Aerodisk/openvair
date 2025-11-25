"""Custom exceptions for XML data handling.

This module defines a hierarchy of custom exceptions for handling errors
that may occur during various XML operations, such as reading, writing,
serialization, and deserialization.

Classes:
    XMLHandlerError: Base exception for all XML-related errors.
    XMLReadingError: Raised when an error occurs while reading an XML file.
    XMLWritingError: Raised when an error occurs while writing an XML file.
    XMLSerializationError: Raised when an error occurs during XML serialization.
    XMLDeserializationError: Raised when an error occurs during XML
        deserialization.
"""

from openvair.abstracts.base_exception import BaseCustomException


class XMLHandlerError(BaseCustomException):
    """Base exception for all XML-related errors."""

    ...


class XMLReadingError(XMLHandlerError):
    """Raised when an error occurs while reading an XML file"""

    ...


class XMLWritingError(XMLHandlerError):
    """Raised when an error occurs while writing an XML file."""

    ...


class XMLSerializationError(XMLHandlerError):
    """Exception raised for errors during XML serialization."""

    ...


class XMLDeserializationError(XMLHandlerError):
    """Exception raised for errors during XML deserialization."""

    ...
