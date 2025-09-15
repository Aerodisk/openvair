"""Configuration for integration tests.

Defines:
- `StorageSettings`: For volume tests (e.g. storage path, fs type).
- `BlockDeviceSettings`: Environment-based settings (e.g. ip, port, inf_type).
- `NotificationSettings`: For notification tests (SMTP credentials).
"""

from __future__ import annotations

from typing import Any, List, Optional
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


class BlockDeviceSettings(BaseSettings):
    """Pydantic settings for testing block_device.

    Attributes:
        ip (str): IP adress of the testing block_device.
        port (str): Port of the testing block_device.
        inf_type (str): Interface type of the testing block_device.
    """

    ip: Optional[str] = Field(default=None, alias='TEST_BLOCK_DEVICE_IP')
    port: str = Field(default='ext4', alias='TEST_BLOCK_DEVICE_PORT')
    inf_type: str = Field(default='ext4', alias='TEST_BLOCK_DEVICE_INF_TYPE')

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

    @field_validator('target_emails', mode='before')
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


class NetworkSettings(BaseSettings):
    """Pydantic settings for network tests.

    Attributes:
        network_interface (str): Physical network interface for bridge tests.
    """

    network_interface: str = Field(
        default='eth0', alias='TEST_NETWORK_INTERFACE'
    )

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent / '.env.test',
        env_file_encoding='utf-8',
        extra='ignore',
    )


storage_settings = StorageSettings()
block_device_settings = BlockDeviceSettings()
notification_settings = NotificationSettings()
network_settings = NetworkSettings()
