"""XML serialization utilities.

This module provides functions for serializing Python data structures into
XML-formatted strings and deserializing XML strings into JSON-compatible.

Functions:
    serialize_xml: Converts a dictionary, list, or primitive type into an XML
        string.
    deserialize_xml: Converts an XML string into a JSON-compatible dictionary or
        list.
"""

from typing import Any, Dict, Optional
from xml.parsers.expat import ExpatError

import xmltodict

from openvair.libs.data_handlers.xml.exceptions import (
    XMLSerializationError,
    XMLDeserializationError,
)


def serialize_xml(
    data: Any,  # noqa: ANN401 # XML can contain various data types (dict, list, etc.)
    *,
    pretty: bool = False,
) -> str:
    """Serialize a Python data structure into an XML string.

    This function converts a dictionary, list, or primitive type (e.g., str,
        int, float)
    into a properly formatted XML string. If the data is a list or a primitive
        type, it is wrapped in a root element.

    Args:
        data (Any): The data to convert into XML. Must be a dictionary, list,
            or a primitive type (e.g., str, int, float).
        pretty (bool, optional): Whether to format the XML output for
            readability. Defaults to False.

    Returns:
        str: The XML-formatted string.

    Raises:
        XMLSerializationError: If the input data is not a valid XML-compatible
            structure.
    """
    if not isinstance(data, (dict, list, str, int, float)):
        message = f'Invalid data type for XML serialization: {type(data)}'
        raise XMLSerializationError(message)

    try:
        xml_string = xmltodict.unparse({'root': data}, pretty=pretty)
        if isinstance(xml_string, str):
            return xml_string

        message = 'Expected XML string but got unexpected type.'
        raise XMLSerializationError(message)
    except (TypeError, ValueError) as e:
        message = f'Invalid data for XML serialization: {e}'
        raise XMLSerializationError(message) from e


def deserialize_xml(
    xml_string: str,
    *,
    preserve_xml_structure: bool = False,
    attr_prefix: Optional[str] = None,
    cdata_key: Optional[str] = None,
) -> Any:  # noqa: ANN401 # XML can contain various data types (dict, list, etc.)
    """Deserialize an XML string into a JSON-compatible data structure.

    This function parses XML into a Python dictionary, list, or primitive type.
    It provides an option to preserve XML attributes and CDATA sections.

    Args:
        xml_string (str): The XML string to parse.
        preserve_xml_structure (bool, optional): If True, retains XML-specific
            metadata (`@` for attributes, `#text` for CDATA). Defaults to False.
        attr_prefix (Optional[str], optional): Custom prefix for XML attributes.
            If None, behavior is determined by `preserve_xml_structure`.
        cdata_key (Optional[str], optional): Custom key for CDATA sections.
            If None, behavior is determined by `preserve_xml_structure`.

    Returns:
        Any: JSON-compatible data structure (dict, list, or primitive type).

    Raises:
        XMLDeserializationError: If the XML string is invalid or cannot be
            parsed.
    """
    try:
        parse_params: Dict[str, Any] = {
            'attr_prefix': '@' if preserve_xml_structure else '',
            'cdata_key': '#text' if preserve_xml_structure else '',
        }

        if attr_prefix is not None:
            parse_params['attr_prefix'] = attr_prefix
        if cdata_key is not None:
            parse_params['cdata_key'] = cdata_key

        return xmltodict.parse(xml_string, **parse_params)
    except ExpatError as e:
        message = f'Malformed XML input: {e}'
        raise XMLDeserializationError(message) from e
    except (TypeError, ValueError) as e:
        message = f'Invalid XML format: {e}'
        raise XMLDeserializationError(message) from e
