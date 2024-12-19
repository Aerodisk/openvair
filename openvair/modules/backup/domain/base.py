"""Base module for backup domain entities.

Defines abstract base classes and models used in the backup domain,
providing interfaces and structures for backup and restore operations.

Classes:
    BaseBackuper: Abstract base class for implementing backup logic.
    FSBackuper: Base class for file-system-based backups.
    DBBackuper: Base class for database backups.
"""

from abc import ABCMeta, abstractmethod
from typing import Dict, List, Union
from pathlib import Path


class BaseBackuper(metaclass=ABCMeta):
    """Abstract base class for implementing backup logic.

    Methods:
        backup: Abstract method for implementing backup logic.
        restore: Abstract method for implementing restore logic.
    """

    @abstractmethod
    def backup(self) -> Dict[str, Union[str, int]]:
        """For implementing backup logic"""
        ...

    @abstractmethod
    def restore(self, data: Dict[str, str]) -> Dict[str, Union[str, int]]:
        """For implementing restore logic"""
        ...


class FSBackuper(BaseBackuper):
    """Base class for file-system-based backups.

    Attributes:
        source_path (Path): Path to the source directory or file to be backed
            up.
    """

    def __init__(self, source_path: str) -> None:
        """Initialize an FSBackuper instance.

        Args:
            source_path (str): Path to the source directory or file to be backed
                up.
        """
        self.source_path = Path(source_path)

    @abstractmethod
    def init_repository(self) -> None:
        """Initialize a backup repository.

        This abstract method should be implemented by subclasses to initialize
        the repository used for storing backups.
        """
        ...

    @abstractmethod
    def get_snapshots(self) -> List[Dict]:
        """Retrieve a list of snapshots.

        This abstract method should be implemented by subclasses to fetch
        metadatafor available snapshots in the repository.

        Returns:
            List[Dict]: A list of snapshot metadata, where each snapshot is
                represented as a dictionary.
        """
        ...
