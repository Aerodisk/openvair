from typing import Dict, Union, NoReturn
from pathlib import Path

from sqlalchemy import text

from openvair.config import (
    get_postgres_uri,
    get_default_session_factory,
)
from openvair.libs.log import get_logger
from openvair.libs.cli.models import ExecuteParams
from openvair.libs.cli.executor import execute
from openvair.modules.backup.domain.base import DBBackuper

LOG = get_logger(__name__)


class PostgresBackuper(DBBackuper):
    def __init__(self, container_name: str, backup_dir: str) -> None:
        self.container_name = container_name
        self.backup_dir = Path(backup_dir)
        self.db_uri = get_postgres_uri()

        # Разбираем URI для получения параметров базы данных
        from sqlalchemy.engine.url import make_url

        db_config = make_url(self.db_uri)
        self.db_user = db_config.username
        self.db_name = db_config.database

        # Создаем фабрику сессий для выполнения операций через SQLAlchemy
        self.session_factory = get_default_session_factory()

    def backup(self) -> Dict[str, Union[str, int]]:
        """Создает резервную копию базы данных.

        Returns:
            Dict[str, str | int]: Результат выполнения, включая путь к файлу.
        """
        try:
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            backup_file = self.backup_dir / f'backup_{self.db_name}.sql'
            command = (
                f'docker exec -t {self.container_name} pg_dump -U '
                f'{self.db_user} -d {self.db_name} > {backup_file}'
            )
            LOG.info(f'Executing backup command: {command}')
            execute(
                command,
                params=ExecuteParams(shell=True, raise_on_error=True),  # noqa: S604
            )
            LOG.info(f'Backup created successfully: {backup_file}')
            return {'status': 'success', 'backup_file': str(backup_file)}
        except Exception as e:
            LOG.error(f'Backup failed: {e!s}')
            return {'status': 'error', 'error': str(e)}

    def restore(self, data: Dict[str, str]) -> Dict[str, Union[str, int]]:
        try:
            backup_file = Path(data.get('backup_file', ''))
            if not backup_file.exists():
                self._raise_error('Backup file not found or not specified.')

            # Завершаем подключения
            with self.session_factory().connection() as conn:
                conn.execute(
                    text("""
                        SELECT pg_terminate_backend(pg_stat_activity.pid)
                        FROM pg_stat_activity
                        WHERE pg_stat_activity.datname = :db_name
                        AND pid <> pg_backend_pid();
                    """),
                    {'db_name': self.db_name},
                )
                LOG.info('Terminated active connections to the database.')

            # Удаляем базу данных
            with self.session_factory().connection() as conn:
                conn.execute(
                    text('DROP DATABASE :db_name;'), {'db_name': self.db_name}
                )
                LOG.info('Dropped the database.')

            # Создаем базу данных
            with self.session_factory().connection() as conn:
                conn.execute(
                    text('CREATE DATABASE :db_name;'), {'db_name': self.db_name}
                )
                LOG.info('Created the database.')

            # Восстанавливаем из файла
            restore_command = (
                f'docker exec -i {self.container_name} psql -U {self.db_user} '
                f'-d {self.db_name} < {backup_file}'
            )
            LOG.info(f'Executing restore command: {restore_command}')
            execute(
                restore_command,
                params=ExecuteParams(shell=True, raise_on_error=True),
            )

            LOG.info(f'Database restored successfully from: {backup_file}')
            return {'status': 'success', 'backup_file': str(backup_file)}
        except Exception as e:
            LOG.error(f'Restore failed: {e!s}')
            return {'status': 'error', 'error': str(e)}

    def _raise_error(self, message: str) -> NoReturn:
        LOG.error(message)
        raise ValueError(message)
