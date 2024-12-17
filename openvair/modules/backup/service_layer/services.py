"""Service layer for managing backups."""

from typing import Dict, List, Union
from pathlib import Path

from openvair.config import TMP_DIR, database as db_config
from openvair.libs.log import get_logger
from openvair.libs.cli.models import ExecuteParams
from openvair.libs.cli.executor import execute
from openvair.libs.cli.exceptions import ExecuteError
from openvair.modules.base_manager import BackgroundTasks
from openvair.modules.backup.config import (
    RESTIC_DIR,
    STORAGE_DATA,
    RESTIC_PASSWORD,
    SERVICE_LAYER_DOMAIN_QUEUE_NAME,
)
from openvair.modules.backup.domain.base import FSBackuper
from openvair.libs.messaging.messaging_agents import MessagingClient
from openvair.modules.event_store.entrypoints.crud import EventCrud
from openvair.modules.backup.service_layer.unit_of_work import (
    SqlAlchemyUnitOfWork,
)

LOG = get_logger(__name__)


class BackupServiceLayerManager(BackgroundTasks):
    """Manager for backup operations in the service layer.

    This class manages backup operations by coordinating communication
    between the service layer, domain layer, and the restic adapter.

    Attributes:
        ...
    """

    def __init__(self) -> None:
        super().__init__()
        self.domain_rpc = MessagingClient(
            queue_name=SERVICE_LAYER_DOMAIN_QUEUE_NAME
        )
        self.uow = SqlAlchemyUnitOfWork()
        self.event_store = EventCrud('networks')
        self.backup_file_name = 'backup.sql'

    def create_backup(
        self,
        data: Dict[str, Union[str, int, None]],
    ) -> Dict[str, Union[str, int, None]]:
        """Perform a database backup and trigger ResticBackuper."""
        backuper_type: str = data['backuper']
        container_name: str = data['container_name']

        db_name = db_config['db_name']
        db_user = db_config['user']
        dump = self.__dump_database(
            container_name,
            db_name,
            db_user,
        )
        self.__write_dump(dump)

        source_path = str(STORAGE_DATA)
        restic_path = str(RESTIC_DIR)
        restic_password = str(RESTIC_PASSWORD)
        result = self.domain_rpc.call(
            FSBackuper.backup.__name__,
            data_for_manager={
                'backuper_type': backuper_type,
                'backuper_data': {
                    'source_path': source_path,
                    'restic_path': restic_path,
                    'restic_password': restic_password,
                },
            },
            data_for_method={},
        )
        return result

    def __dump_database(
        self,
        container_name: str,
        db_name: str,
        db_user: str,
    ) -> str:
        command = (
            f'docker exec -t {container_name} '
            f'pg_dump -U {db_user} -d {db_name}'
        )
        with self.uow:
            self.uow.repository.terminate_all_connections(db_config['db_name'])
            try:
                LOG.info('Dumping database...')
                dump_result = execute(
                    command,
                    params=ExecuteParams(  # noqa: S604
                        shell=True,
                        run_as_root=True,
                        raise_on_error=True,
                    ),
                )
                LOG.info('Database dump complete success')
            except (ExecuteError, OSError) as err:
                LOG.error(f'Error while backuping DB: {err!s}')
                raise
            else:
                return dump_result.stdout

    def __write_dump(self, dump: str) -> None:
        LOG.info('Writing dump to tmp dir...')

        backup_file = Path(TMP_DIR) / self.backup_file_name
        with backup_file.open('w') as f:
            f.write(dump)
        LOG.info('Dump seccuessfull written into tmp')

        LOG.info('Moving dump file into project data dir...')
        move_cmd = f'mv {backup_file} {STORAGE_DATA}'
        execute(
            move_cmd,
            params=ExecuteParams(  # noqa: S604
                shell=True,
                run_as_root=True,
                raise_on_error=True,
            ),
        )
        LOG.info('Dump successfuul moved into project data folder')

