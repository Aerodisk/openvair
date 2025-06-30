"""Schemas for backup domain operations.

This module defines Pydantic models for data validation and parsing
in backup-related operations. These schemas are used for representing
backup results, restore results, and snapshot metadata across the
application.
"""

from typing import List, Optional

from pydantic import BaseModel

from openvair.modules.backup.config import (
    RESTIC_DIR,
    STORAGE_DATA,
    RESTIC_PASSWORD,
)


class ResticBackupResult(BaseModel):
    """Schema for restic backup results.

    This schema represents the results of a backup operation and includes
    metadata about the files processed and data added during the backup.

    Attributes:
        snapshot_id (Optional[str]): ID of the created snapshot, if available.
        total_files_processed (int): Total number of files processed.
        files_new (int): Number of new files backed up.
        files_changed (int): Number of changed files backed up.
        files_unmodified (int): Number of unmodified files.
        data_added_packed (int): Total size of the packed data added, in bytes.
    """

    snapshot_id: Optional[str] = None
    total_files_processed: int
    files_new: int
    files_changed: int
    files_unmodified: int
    data_added_packed: int

    class Config:
        """Pydantic configuration for the model.

        Attributes:
            extra (str): Specifies how to handle extra fields. Set to 'ignore'
                to silently discard any fields not explicitly defined in the
                model.
        """

        extra = 'ignore'


class ResticRestoreResult(BaseModel):
    """Schema for restic restore results.

    This schema represents the results of a restore operation and includes
    metadata about the files and data restored or skipped.

    Attributes:
        total_files (int): Total number of files in the backup.
        files_restored (int): Number of files successfully restored.
        files_skipped (int): Number of files skipped during restore.
        total_bytes (Optional[int]): Total size of the backup, in bytes.
        bytes_restored (Optional[int]): Size of data successfully restored, in
            bytes.
        bytes_skipped (Optional[int]): Size of data skipped during restore, in
            bytes.
    """

    total_files: int
    files_restored: int
    files_skipped: Optional[int] = None # just to try
    total_bytes: Optional[int] = None
    bytes_restored: Optional[int] = None
    bytes_skipped: Optional[int] = None

    class Config:
        """Pydantic configuration for the model.

        Attributes:
            extra (str): Specifies how to handle extra fields. Set to 'ignore'
                to silently discard any fields not explicitly defined in the
                model.
        """

        extra = 'ignore'


class ResticSnapshot(BaseModel):
    """Schema for metadata of a restic snapshot.

    This schema represents metadata about a snapshot stored in the backup
    repository, including its ID, creation timestamp, and associated paths.

    Attributes:
        id (str): Unique ID of the snapshot.
        short_id (str): Shortened ID of the snapshot.
        time (str): Timestamp of the snapshot creation in ISO 8601 format.
        paths (List): List of file or directory paths included in the snapshot.
        hostname (str): Hostname where the snapshot was created.
        username (str): Username of the snapshot creator.
    """

    id: str
    short_id: str
    time: str
    paths: List
    hostname: str
    username: str

    class Config:
        """Pydantic configuration for the model.

        Attributes:
            extra (str): Specifies how to handle extra fields. Set to 'ignore'
                to silently discard any fields not explicitly defined in the
                model.
        """

        extra = 'ignore'


class ResticDeleteResult(BaseModel):
    """Schema for restic snapshot deletion results.

    This schema represents the result of a snapshot deletion operation
    performed using Restic.

    Attributes:
        message (str): A message describing the outcome of the deletion
            operation, including stdout and stderr details.
    """

    message: str


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


class DataForResticManager(ResticBackuperData):
    """Schema for preparing data for the Restic domain manager.

    This schema wraps Restic backuper configuration data along with the
    backuper type, used to identify and manage Restic-related operations.

    Attributes:
        backuper_type (str): Type of the backuper. Defaults to "restic".
        backuper_data (Dict): Configuration data for the Restic backuper,
            generated from the `ResticBackuperData` schema.
    """

    backuper_type: str = 'restic'
