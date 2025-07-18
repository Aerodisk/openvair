"""Configuration for volume integration tests.

Defines:
- `VolumeTestSettings`: Environment-based settings (e.g. storage path, fs type).
- Loads `.env.test` for overrides.
"""

from pathlib import Path

from pydantic import Field
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
        env_file=Path(__file__).parent / '.env.test', env_file_encoding='utf-8'
    )


storage_settings = StorageSettings()
