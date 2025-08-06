"""Configuration for integration tests.

Defines:
- `StorageSettings`: For volume tests (e.g. storage path, fs type).
- `NotificationSettings`: For notification tests (SMTP credentials).
- Loads `.env.test` for overrides.
"""
from __future__ import annotations

from typing import Any, List
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class StorageSettings(BaseSettings):
    """Pydantic settings for test storage environment.

    Attributes:
        storage_path (Path): Filesystem path to use for test storage.
        storage_fs_type (str): Filesystem type (e.g. ext4, xfs).
    """
    storage_path: Path = Field(default=None, alias='TEST_STORAGE_PATH')
    storage_fs_type: str = Field(default='ext4', alias='TEST_STORAGE_FS_TYPE')

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent / '.env.test',
        env_file_encoding='utf-8',
        extra='ignore',
    )


class NotificationSettings(BaseSettings):
    """Pydantic settings for notification tests.

    Attributes:
        target_emails (List[str]): Email for test notifications.
        notification_type (str): Default type (email/sms/etc).
    """
    target_emails: Any = Field(
        default=['test@email.com'], alias='TEST_NOTIFICATION_EMAILS'
    )

    @field_validator("target_emails", mode="before")
    @classmethod
    def convert_to_list(cls, v: str) -> List[str]:
        """Validate the `target_emails` field parsing to list of emails"""
        return [email.strip() for email in v.split(',')]

    notification_type: str = Field(
        default='email', alias='TEST_NOTIFICATION_TYPE'
    )

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent / '.env.test',
        env_file_encoding='utf-8',
        extra='ignore',
    )


storage_settings = StorageSettings()
notification_settings = NotificationSettings()
