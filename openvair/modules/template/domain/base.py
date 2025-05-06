"""Base classes for template domain models.

This module defines the `BaseTemplate` abstract class, which serves as the
foundation for implementing specific template types (e.g., QCOW2). It declares
the required interface and shared fields used for managing templates.
"""

import abc
from typing import Dict, List, Optional
from pathlib import Path

from openvair.libs.qemu_img.adapter import QemuImgAdapter


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

    def __init__(
        self,
        tmp_format: str,
        name: str,
        path: Path,
        related_volumes: Optional[List],
        *,
        is_backing: bool,
    ) -> None:
        """Initialize base attributes for a template.

        Sets up the QEMU image adapter and defines default fields to be used
        by subclasses (e.g., template format, name, path, related volumes).
        """
        self.qemu_img_adapter = QemuImgAdapter()
        self.tmp_format = tmp_format
        self.name = name
        self.path = path
        self.related_volumes = related_volumes
        self.is_backing = is_backing

    @abc.abstractmethod
    def create(self, creation_data: Dict) -> Dict:
        """Create the template on disk.

        Args:
            creation_data (Dict): Data required for template creation.
        """
        ...

    @abc.abstractmethod
    def edit(self, editing_data: Dict) -> Dict:
        """Edit the template metadata or file.

        Args:
            editing_data (Dict): Data for modifying the template.
        """
        ...

    @abc.abstractmethod
    def delete(self) -> None:
        """Delete the template file from disk."""
        ...
