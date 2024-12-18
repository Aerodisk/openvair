"""Service layer for managing backups."""

from typing import Any, Dict, List, Union
from pathlib import Path

from openvair.config import TMP_DIR, DB_CONTAINER, database as db_config
from openvair.libs.log import get_logger
from openvair.libs.cli.models import ExecuteParams
from openvair.libs.cli.executor import execute
from openvair.libs.cli.exceptions import ExecuteError
from openvair.modules.base_manager import BackgroundTasks
from openvair.modules.backup.config import (
    STORAGE_DATA,
    BACKUPER_TYPE,
    SERVICE_LAYER_DOMAIN_QUEUE_NAME,
)
from openvair.modules.backup.domain.base import FSBackuper
from openvair.libs.messaging.messaging_agents import MessagingClient
from openvair.modules.backup.service_layer.schemas import DataForResticManager
from openvair.modules.event_store.entrypoints.crud import EventCrud
from openvair.modules.backup.service_layer.exceptions import (
    WrongBackuperTypeError,
)
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

    def create_backup(self) -> Dict[str, Union[str, int, None]]:
        """Perform a database backup and trigger ResticBackuper."""
        dump = self.__dump_database()
        self.__write_dump(dump)

        result = self.domain_rpc.call(
            FSBackuper.backup.__name__,
            data_for_manager=self.__create_data_for_domain_manager(),
            data_for_method={},
        )
        return result

    def restore_backup(self, data: Dict[str, Union[str, int, None]]) -> Dict:
        """Restore data using a specific snapshot ID."""
        self.__restore_db()
        result = self.domain_rpc.call(
            FSBackuper.restore.__name__,
            data_for_manager=self.__create_data_for_domain_manager(),
            data_for_method={},
        )
        return {}

    def get_snapshots(self) -> List[str]:
        """Retrieve a list of available snapshots."""

        result = self.domain_rpc.call(
            FSBackuper.get_snapshots.__name__,
            data_for_manager=self.__create_data_for_domain_manager(),
            data_for_method={},
        )
        return result

    def initialize_backup_repository(self) -> Dict:
        """Initialize the backup repository using ResticBackuper."""
        result = self.domain_rpc.call(
            FSBackuper.init_repository.__name__,
            data_for_manager=self.__create_data_for_domain_manager(),
            data_for_method={},
        )
        return {}

    def __dump_database(
        self,
    ) -> str:
        db_name = db_config['db_name']
        db_user = db_config['user']
        command = (
            f'docker exec -t {DB_CONTAINER} '
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

    def __restore_db(self) -> None:
        backup_file = str(STORAGE_DATA / self.backup_file_name)
        db_name: str = db_config['db_name']
        db_user: str = db_config['db_user']
        with self.uow:
            self.uow.repository.terminate_all_connections(db_name)
            self.uow.commit()

            self.uow.repository.drop_db(db_name)

            self.uow.repository.create_db(db_name)

            restore_command = (
                f'docker exec -i {DB_CONTAINER} psql -U {db_user} '
                f'-d {db_name} < {backup_file}'
            )
            LOG.info(f'Executing restore command: {restore_command}')
            try:
                execute(
                    restore_command,
                    params=ExecuteParams(shell=True, raise_on_error=False),
                )
            except (ExecuteError, OSError) as err:
                LOG.error(f'{err!s}')
                raise

            LOG.info(f'Database restored successfully from: {backup_file}')

    def __create_data_for_domain_manager(self) -> Dict[str, Any]:
        if BACKUPER_TYPE == 'restic':
            return DataForResticManager().model_dump()
        message = f'Unknown backuper type: {BACKUPER_TYPE}.'
        LOG.error(message)
        raise WrongBackuperTypeError(message)
