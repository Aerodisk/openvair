"""XML serialization utilities.

This module provides functions for serializing and deserializing XML-compatible
data structures, ensuring JSON compatibility by normalizing keys.

Functions:
    serialize_xml: Serializes a Python dictionary into an XML-formatted string.
    deserialize_xml: Deserializes an XML-formatted string into a JSON-compatible
        dictionary.
"""

from typing import Any, Dict, List, Union, OrderedDict
from xml.parsers.expat import ExpatError

import xmltodict

from openvair.libs.data_handlers.xml.exceptions import (
    XMLSerializationError,
    XMLDeserializationError,
)


def serialize_xml(data: Dict[str, Any]) -> str:
    """Serialize a Python dictionary into an XML string.

    Args:
        data (Dict[str, Any]): The data to convert.

    Returns:
        str: XML-formatted string.

    Raises:
        XMLSerializationError: If data is not a valid XML-compatible type.
    """
    try:
        xml_string = xmltodict.unparse(data, pretty=True)
        if isinstance(xml_string, str):
            return xml_string

        message = 'Expected XML string but got unexpected type.'
        raise XMLSerializationError(message)
    except (TypeError, ValueError) as e:
        message = f'Invalid data for XML serialization: {e}'
        raise XMLSerializationError(message) from e


def _parse_xml(xml_string: str) -> Union[OrderedDict[str, Any], List[Any]]:
    """Parse XML string and return structured data.

    Args:
        xml_string (str): The XML string to parse.

    Returns:
        Union[OrderedDict[str, Any], List[Any]]: Parsed XML data.

    Raises:
        XMLDeserializationError: If the XML string is invalid.
    """
    try:
        parsed_data = xmltodict.parse(xml_string)
        if isinstance(parsed_data, (OrderedDict, list)):
            return parsed_data
        message = 'Unexpected type returned from XML parsing.'
        raise XMLDeserializationError(message)
    except ExpatError as e:
        message = f'Malformed XML input: {e}'
        raise XMLDeserializationError(message) from e
    except ValueError as e:
        message = f'Invalid XML format: {e}'
        raise XMLDeserializationError(message) from e


def _remove_prefix(
    d: Union[OrderedDict[str, Any], List[Any]],
) -> Union[Dict[str, Any], List[Any]]:
    """Recursively remove '@' prefix for keys in parsed XML data.

    Args:
        d (Union[OrderedDict[str, Any], List[Any]]): Parsed XML data.

    Returns:
        Union[Dict[str, Any], List[Any]]: Data with normalized keys.
    """
    if isinstance(d, dict):
        return {k.lstrip('@'): _remove_prefix(v) for k, v in d.items()}
    if isinstance(d, list):
        return [_remove_prefix(i) for i in d]
    return d


def deserialize_xml(xml_string: str) -> Union[Dict[str, Any], List[Any]]:
    """Deserialize an XML string into a JSON-compatible dictionary.

    This function parses XML into a dictionary and removes `@` prefixes from
    keys.

    Args:
        xml_string (str): The XML string to parse.

    Returns:
        Union[Dict[str, Any], List[Any]]: JSON-compatible dictionary or list.

    Raises:
        XMLDeserializationError: If the XML string is invalid.
    """
    parsed_dict = _parse_xml(xml_string)
    return _remove_prefix(parsed_dict)
