"""Base classes for template domain models.

This module defines the `BaseTemplate` abstract class, which serves as the
foundation for implementing specific template types (e.g., QCOW2). It declares
the required interface and shared fields used for managing templates.
"""

import abc
from typing import TYPE_CHECKING, Dict, List

from openvair.libs.qemu_img.adapter import QemuImgAdapter

if TYPE_CHECKING:
    from pathlib import Path


class BaseTemplate(metaclass=abc.ABCMeta):
    """Abstract base class for template domain models.

    This class defines the interface for all template operations such as
    creation, editing, and deletion. Concrete implementations must implement
    all abstract methods.

    Attributes:
        qemu_img_adapter (QemuImgAdapter): Utility for performing disk-level
            operations.
        format (str): Disk format (default: 'qcow2').
        name (str): Name of the template.
        path (Path): Filesystem path to the template image.
        related_volumes (List): List of volumes created from this template.
        is_backing (bool): Indicates if the template is a backing image.
    """

    def __init__(self) -> None:
        """Initialize base attributes for a template.

        Sets up the QEMU image adapter and defines default fields to be used
        by subclasses (e.g., template format, name, path, related volumes).
        """
        self.qemu_img_adapter = QemuImgAdapter()
        self.format: str = 'qcow2'
        self.name: str
        self.path: Path
        self.related_volumes: List
        self.is_backing: bool

    @abc.abstractmethod
    def create(self, creation_data: Dict) -> None:
        """Create the template on disk.

        Args:
            creation_data (Dict): Data required for template creation.
        """
        ...

    @abc.abstractmethod
    def edit(self, editing_data: Dict) -> None:
        """Edit the template metadata or file.

        Args:
            editing_data (Dict): Data for modifying the template.
        """
        ...

    @abc.abstractmethod
    def delete(self) -> None:
        """Delete the template file from disk."""
        ...
