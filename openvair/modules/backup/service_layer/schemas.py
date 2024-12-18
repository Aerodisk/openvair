"""Schemas for data validation and configuration in the service layer.

This module defines Pydantic models for managing and validating
configuration data used in the backup service layer. These schemas
help ensure proper data structures are passed between components.
"""

from typing import Dict

from pydantic import BaseModel

from openvair.modules.backup.config import (
    RESTIC_DIR,
    STORAGE_DATA,
    RESTIC_PASSWORD,
)


class ResticBackuperData(BaseModel):
    """Schema for Restic backuper configuration data.

    This schema defines default paths and passwords required to configure
    a Restic backuper.

    Attributes:
        source_path (str): Path to the source data to be backed up. Defaults
            to the `STORAGE_DATA` configuration value.
        restic_path (str): Path to the Restic repository. Defaults to the
            `RESTIC_DIR` configuration value.
        restic_password (str): Password for the Restic repository. Defaults
            to the `RESTIC_PASSWORD` configuration value.
    """

    source_path: str = str(STORAGE_DATA)
    restic_path: str = str(RESTIC_DIR)
    restic_password: str = str(RESTIC_PASSWORD)


class DataForResticManager(BaseModel):
    """Schema for preparing data for the Restic domain manager.

    This schema wraps Restic backuper configuration data along with the
    backuper type, used to identify and manage Restic-related operations.

    Attributes:
        backuper_type (str): Type of the backuper. Defaults to "restic".
        backuper_data (Dict): Configuration data for the Restic backuper,
            generated from the `ResticBackuperData` schema.
    """

    backuper_type: str = 'restic'
    backuper_data: Dict = ResticBackuperData().model_dump()
