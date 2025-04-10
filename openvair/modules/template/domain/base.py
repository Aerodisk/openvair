"""Base classes for template domain models.

This module defines abstract base classes for template-related domain models,
providing a foundation for different template types.
"""

import abc
from typing import TYPE_CHECKING, Dict

from openvair.libs.qemu_img.adapter import QemuImgAdapter

if TYPE_CHECKING:
    from pathlib import Path


class BaseTemplate(metaclass=abc.ABCMeta):
    """Abstract base class for template models."""

    def __init__(self) -> None:  # noqa: D107
        self.qemu_img_adapter = QemuImgAdapter()
        self.format: str = 'qcow2'
        self.name: str
        self.path: Path
        self.is_backing: bool

    @abc.abstractmethod
    def create(self) -> Dict:  # noqa: D102
        ...

    @abc.abstractmethod
    def edit(self) -> Dict:  # noqa: D102
        ...

    @abc.abstractmethod
    def delete(self) -> Dict:  # noqa: D102
        ...

