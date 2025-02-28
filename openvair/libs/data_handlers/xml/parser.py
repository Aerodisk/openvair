"""XML file parsing utilities.

This module provides helper functions for reading and writing XML files.

Functions:
    read_xml: Reads an XML file and returns its parsed content as a dictionary.
    write_xml: Writes a dictionary or list to an XML file.
"""

from typing import Any
from pathlib import Path

from openvair.libs.data_handlers.xml.exceptions import (
    XMLReadingError,
    XMLWritingError,
    XMLSerializationError,
    XMLDeserializationError,
)
from openvair.libs.data_handlers.xml.serializer import (
    serialize_xml,
    deserialize_xml,
)


def read_xml(file_path: Path) -> Any:  # noqa: ANN401 # XML can contain various data types (dict, list, etc.)
    """Read an XML file and return its parsed content as a dictionary.

    This function loads an XML file from the specified path and converts it
    into a JSON-compatible structure (usually a dictionary or list).

    Args:
        file_path (Path): The path to the XML file.

    Returns:
        Any: Parsed XML data as a dictionary, list, or other primitive types.

    Raises:
        XMLReadingError: If the file is not found or the XML is invalid.
    """
    if not file_path.exists():
        message = f'XML file not found: {file_path}'
        raise XMLReadingError(message)

    try:
        with file_path.open('r', encoding='utf-8') as f:
            return deserialize_xml(f.read())
    except (OSError, XMLDeserializationError) as e:
        message = f'Error reading XML file {file_path}: {e}'
        raise XMLReadingError(message) from e


def write_xml(
    file_path: Path,
    data: Any,  # noqa: ANN401 # XML can contain various data types (dict, list, etc.)
    *,
    pretty: bool = False,
    wrap_root: bool = True,
) -> None:
    """Write a dictionary, list, or primitive type as an XML file.

    This function serializes Python data into an XML file.

    **Root Wrapping (`wrap_root`)**:
    - `wrap_root=True` (default): Wraps lists and primitives into `<root>`.
    - `wrap_root=False`: Serializes dictionaries as is.

    Example:
        ```python
        write_xml('example.xml', {'name': 'Alice', 'age': 30})
        ```
        Produces:
        ```xml
        <root>
            <name>Alice</name>
            <age>30</age>
        </root>
        ```

    Args:
        file_path (Path): The path of the XML file to write.
        data (Any): The data to serialize into XML. Must be a dictionary, list,
            or a primitive type (e.g., str, int, float).
        pretty (bool, optional): Whether to format the XML output for
            readability. Defaults to False.
        wrap_root (bool, optional): Whether to wrap non-dict data in `<root>`.
            Defaults to True.

    Raises:
        XMLWritingError: If an error occurs while writing the file.
    """
    try:
        xml_content = serialize_xml(data, pretty=pretty, wrap_root=wrap_root)
        with file_path.open('w', encoding='utf-8') as f:
            f.write(xml_content)
    except (OSError, XMLSerializationError) as e:
        message = f'Error writing XML file {file_path}: {e}'
        raise XMLWritingError(message) from e
