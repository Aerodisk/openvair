"""Adapter for interacting with restic by executing bash command.

This module provides the `ResticAdapter` class, which is used to manage
backuping through the restic app.

Classes:
    ResticAdapter: Adapter class for managing backups.
"""

from typing import TYPE_CHECKING

from openvair.modules.backup import config
from openvair.modules.backup.adapters.restic_executor import (
    ResticCommandExecutor,
)

if TYPE_CHECKING:
    from pathlib import Path


class ResticAdapter:
    """Provides business logic for interacting with restic."""

    def __init__(self) -> None:
        """Initialize ResticAdapter instance."""
        self.restic_dir: Path = config.RESTIC_DIR
        self.restic_pass: str = config.RESTIC_PASSWORD
        self.executor = ResticCommandExecutor(
            str(self.restic_dir),
            self.restic_pass,
        )

    def init_repository(self) -> bool:
        result = self.executor.init_repository()

