"""Module for providing abstract base classes for backup domain entities."""

from abc import ABCMeta, abstractmethod
from typing import Dict, List, Optional
from pathlib import Path


class BaseBackuper(metaclass=ABCMeta):
    """Base class for backup domain entities

    Attributes:
        repository (Path): Path to the repository with backups
    """

    def __init__(self, repository: Path) -> None:
        """Initializes a new backuper entity

        Args:
            repository (Path): Path to the repository with backups
        """
        self.repository = repository

    @abstractmethod
    def do_backup(
        self,
        *,
        paths: List[Path],
        tags: Optional[List[str]],
    ) -> Dict[str, str]:
        """For implementing backup logic"""
        ...

    @abstractmethod
    def restore(
        self,
        *,
        paths: List[Path],
        tags: Optional[List[str]],
    ) -> Dict[str, str]:
        """For implementing restore logic"""
        ...
