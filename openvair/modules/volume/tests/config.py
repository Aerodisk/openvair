from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class VolumeTestSettings(BaseSettings):  # noqa: D101
    storage_path: Path = Field(default=None, alias='TEST_STORAGE_PATH')
    storage_fs_type: str = Field(default='ext4', alias='TEST_STORAGE_FS_TYPE')

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent / '.env.test', env_file_encoding='utf-8'
    )


settings = VolumeTestSettings()
