"""Serialize a Python data structure into an XML string.

This function converts a dictionary, list, or primitive type (e.g., str,
int, float) into a properly formatted XML string.

By default, lists and primitive types are wrapped in a `<root>` element:
- `serialize_xml("text")` → `<root>text</root>`
- `serialize_xml([1, 2, 3])` → `<root><item>1</item><item>2</item></root>`

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

from typing import Any, Dict, Optional
from xml.parsers.expat import ExpatError

import xmltodict

from openvair.libs.data_handlers.xml.exceptions import (
    XMLSerializationError,
    XMLDeserializationError,
)


def serialize_xml(
    data: Any, # noqa: ANN401 # XML can contain various data types (dict, list, etc.)
    *,
    pretty: bool = False,
    wrap_root: bool = True,
) -> str:
    """Serialize a Python data structure into an XML string.

    This function converts a dictionary, list, or primitive type (e.g., str,
    int, float) into a properly formatted XML string.

    - If `wrap_root=True`, lists and primitive types are wrapped in a `<root>`
        element:
            - `serialize_xml("text")` → `<root>text</root>`
            - `serialize_xml([1, 2, 3])` → `<root><item>1</item><item>2</item></root>`

    - If `wrap_root=False`, only dictionaries are serialized directly.
        - `serialize_xml({"name": "Alice"})` → `<name>Alice</name>`

    Args:
        data (Any): The data to convert into XML. Must be a dictionary, list,
            or a primitive type (e.g., str, int, float).
        pretty (bool, optional): Whether to format the XML output for
            readability. Defaults to False.
        wrap_root (bool, optional): Whether to wrap non-dict data in `<root>`.
            Defaults to True.

    Returns:
        str: The XML-formatted string.

    Raises:
        XMLSerializationError: If the input data is not a valid XML-compatible
            structure.
    """  # noqa: E501
    try:
        if wrap_root and not isinstance(data, Dict):
            data = {'root': data}

        xml_string = xmltodict.unparse(data, pretty=pretty)
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
    attr_prefix: Optional[str] = '@',
    cdata_key: Optional[str] = '#text',
) -> Any:  # noqa: ANN401 # XML can contain various data types (dict, list, etc.)
    """Deserialize an XML string into a JSON-compatible data structure.

    This function parses XML into a Python dictionary, list, or primitive type.

    **Attribute Handling (`attr_prefix`)**:
    - By default, attributes in XML (e.g., `<tag key="value">`) are prefixed
        with `@`:
            ```xml
            <item key="1">value</item>
            ```
            Converts to:
            ```json
            {"item": {"@key": "1", "#text": "value"}}
            ```

    - If `attr_prefix=''`, attributes become normal dictionary keys:
        ```json
        {"item": {"key": "1", "#text": "value"}}
        ```

    **CDATA Handling (`cdata_key`)**:
    - CDATA sections are stored under `#text`:
        ```xml
        <description><![CDATA[Some Text]]></description>
        ```
        Converts to:
        ```json
        {"description": {"#text": "Some Text"}}
        ```

    Args:
        xml_string (str): The XML string to parse.
        attr_prefix (Optional[str], optional): Custom prefix for XML attributes.
            Defaults to `@`. Set to `''` to remove prefixes.
        cdata_key (Optional[str], optional): Custom key for CDATA sections.
            Defaults to `#text`. Set to `''` to ignore CDATA.

    Returns:
        Any: JSON-compatible data structure (dict, list, or primitive type).

    Raises:
        XMLDeserializationError: If the XML string is invalid or cannot be
            parsed.
    """
    try:
        return xmltodict.parse(
            xml_string, attr_prefix=attr_prefix, cdata_key=cdata_key
        )
    except ExpatError as e:
        message = f'Malformed XML input: {e}'
        raise XMLDeserializationError(message) from e
    except (TypeError, ValueError) as e:
        message = f'Invalid XML format: {e}'
        raise XMLDeserializationError(message) from e
