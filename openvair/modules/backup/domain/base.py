"""Module for providing abstract base classes for backup domain entities."""

from abc import ABCMeta, abstractmethod
from typing import Any, Dict, List, Union, Optional
from pathlib import Path

from pydantic import BaseModel


class BackupData(BaseModel):
    """Base model for data to be backed up."""

    data: Dict[str, Any]  # JSON-compatible structure
    metadata: Optional[Dict[str, Any]] = None  # Optional metadata


class BaseBackuper(metaclass=ABCMeta):
    """Base class for backup domain entities"""

    @abstractmethod
    def backup(self) -> Dict[str, Union[str, int]]:
        """For implementing backup logic"""
        ...

    @abstractmethod
    def restore(self, data: Dict[str, str]) -> Dict[str, Union[str, int]]:
        """For implementing restore logic"""
        ...


class FSBackuper(BaseBackuper):
    def __init__(self, source_path: str) -> None:
        self.source_path = Path(source_path)

    @abstractmethod
    def init_repository(self) -> Dict[str, str]: ...

    @abstractmethod
    def get_snapshots(self) -> List[Dict]: ...


class DBBackuper(BaseBackuper): ...
