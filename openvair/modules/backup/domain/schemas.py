"""Schemas for backup domain operations.

Defines data models for representing results and snapshots used in
backup operations, leveraging Pydantic for data validation and parsing.

Classes:
    ResticBackupResult: Schema for backup results.
    ResticRestoreResult: Schema for restore results.
    ResticSnapshot: Schema for snapshots metadata.
"""
from typing import List, Optional

from pydantic import BaseModel


class ResticBackupResult(BaseModel):
    """Schema for restic backup results.

    Attributes:
        snapshot_id (Optional[str]): ID of the created snapshot, if available.
        total_files_processed (int): Total number of files processed.
        files_new (int): Number of new files backed up.
        files_changed (int): Number of changed files backed up.
        files_unmodified (int): Number of unmodified files.
        data_added_packed (int): Size of data added, in bytes.
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

    Attributes:
        total_files (int): Total number of files in the backup.
        files_restored (int): Number of files successfully restored.
        files_skipped (int): Number of files skipped during restore.
        total_bytes (int): Total size of the backup, in bytes.
        bytes_restored (int): Size of data successfully restored, in bytes.
        bytes_skipped (int): Size of data skipped during restore, in bytes.
    """
    total_files: int
    files_restored: int
    files_skipped: int
    total_bytes: int
    bytes_restored: int
    bytes_skipped: int

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

    Attributes:
        id (str): Unique ID of the snapshot.
        short_id (str): Shortened ID of the snapshot.
        time (str): Timestamp of the snapshot creation.
        paths (List): List of paths included in the snapshot.
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
