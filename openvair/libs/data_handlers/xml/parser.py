"""XML file parsing utilities.

This module provides helper functions for reading and writing XML files.

Functions:
    read_xml: Reads an XML file and returns its ElementTree.
    write_xml: Writes an ElementTree to an XML file.
"""

from typing import Union
from pathlib import Path
from xml.etree import ElementTree


def read_xml(file_path: Path) -> ElementTree.ElementTree:
    """Read an XML file and return its ElementTree.

    Args:
        file_path (Path): The path to the XML file.

    Returns:
        ElementTree.ElementTree: Parsed XML tree.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the XML content is invalid.
    """
    if not file_path.exists():
        message = f'XML file not found: {file_path}'
        raise FileNotFoundError(message)

    try:
        return ElementTree.parse(file_path)  # noqa: S314
    except ElementTree.ParseError as e:
        message = f'Error reading XML file {file_path}: {e}'
        raise ValueError(message)


def write_xml(
    file_path: Path,
    xml_tree: Union[ElementTree.Element, ElementTree.ElementTree],
) -> None:
    """Write an XML tree to a file.

    Args:
        file_path (Path): The path of the XML file to write.
        xml_tree (Union[ElementTree.Element, ElementTree.ElementTree]): XML data
            to be written.

    Raises:
        IOError: If writing to the file fails.
    """
    try:
        tree = (
            xml_tree
            if isinstance(xml_tree, ElementTree.ElementTree)
            else ElementTree.ElementTree(xml_tree)
        )
        tree.write(file_path, encoding='utf-8', xml_declaration=True)
    except IOError as e:
        message = f'Error writing XML file {file_path}: {e}'
        raise IOError(message)
