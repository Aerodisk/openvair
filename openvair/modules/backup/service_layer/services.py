"""Service layer for managing backup operations.

This module defines the `BackupServiceLayerManager` class, which orchestrates
backup, restore, repository initialization, and snapshot management operations.
It acts as a bridge between the service layer and domain layer, coordinating
tasks via messaging and background processes.
"""

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
from openvair.modules.backup.schemas import DataForResticManager
from openvair.modules.backup.domain.base import FSBackuper
from openvair.libs.messaging.messaging_agents import MessagingClient
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

    This class coordinates backup, restore, snapshot retrieval, and
    repository initialization processes. It communicates with the domain
    layer using messaging and manages database operations internally.

    Attributes:
        domain_rpc (MessagingClient): Client for interacting with the domain
            layer.
        uow (SqlAlchemyUnitOfWork): Unit of work for managing database
            operations.
        event_store (EventCrud): Event store for recording and retrieving
            events.
        backup_file_name (str): Name of the database backup file.
    """

    def __init__(self) -> None:
        """Initialize a BackupServiceLayerManager instance.

        Sets up messaging clients, unit of work, event storage, and default
        configurations for managing backups.
        """
        super().__init__()
        self.domain_rpc = MessagingClient(
            queue_name=SERVICE_LAYER_DOMAIN_QUEUE_NAME
        )
        self.uow = SqlAlchemyUnitOfWork()
        self.event_store = EventCrud('networks')
        self.backup_file_name = 'backup.sql'

    def create_backup(self) -> Dict[str, Union[str, int, None]]:
        """Perform a database backup and trigger ResticBackuper.

        This method dumps the database, writes the dump to a temporary file,
        and invokes the domain layer to manage further backup operations.

        Returns:
            Dict[str, Union[str, int, None]]: Result of the backup operation,
            as returned by the domain layer.
        """
        LOG.info('Start creating backup')
        dump = self.__dump_database()
        self.__write_dump(dump)

        result: Dict[str, Union[str, int, None]] = self.domain_rpc.call(
            FSBackuper.backup.__name__,
            data_for_manager=self.__create_data_for_domain_manager(),
        )
        LOG.info('Backup successfull created')
        return result

    def delete_snapshot(
        self, data: Dict[str, str]
    ) -> Dict[str, Union[str, int, None]]:
        """_summary_

        Args:
            data (Dict[str, str]): _description_

        Raises:
            NotImplementedError: _description_

        Returns:
            Dict[str, Union[str, int, None]]: _description_
        """
        result: Dict[str, Union[str, int, None]] = self.domain_rpc.call(
            FSBackuper.delete_snapshot.__name__,
            data_for_manager=self.__create_data_for_domain_manager(),
            data_for_method={'snapshot_id': data.get('snapshot_id')},
        )
        return result

    def restore_backup(
        self,
        data: Dict[
            str,
            Union[str, int, None],
        ],
    ) -> Dict[str, Union[str, int, None]]:
        """Restore data using a specific snapshot ID.

        This method restores the database and invokes the domain layer to manage
        additional restore operations.

        Returns:
            Dict[str, Union[str, int, None]]: Result of the restore operation,
                as returned by the domain layer.
        """
        LOG.info('Start restoring backup')
        self.__restore_db()
        result: Dict[str, Union[str, int, None]] = self.domain_rpc.call(
            FSBackuper.restore.__name__,
            data_for_manager=self.__create_data_for_domain_manager(),
            data_for_method={'snapshot_id': data.get('snapshot_id', 'latest')},
        )
        LOG.info('Restoring successfull complete')
        return result

    def get_snapshots(self) -> List[Dict]:
        """Retrieve a list of available snapshots.

        This method queries the domain layer to fetch metadata for available
        snapshots stored in the backup repository.

        Returns:
            List[Dict]: A list of snapshot metadata.
        """
        LOG.info('Getting backup snapshots')
        result: List[Dict] = self.domain_rpc.call(
            FSBackuper.get_snapshots.__name__,
            data_for_manager=self.__create_data_for_domain_manager(),
            data_for_method={},
        )
        LOG.info('Snpashots successfull collected')
        return result

    def initialize_backup_repository(self) -> None:
        """Initialize the backup repository using ResticBackuper.

        This method invokes the domain layer to create and configure the backup
        repository.
        """
        LOG.info('Start initializing repository')
        self.domain_rpc.call(
            FSBackuper.init_repository.__name__,
            data_for_manager=self.__create_data_for_domain_manager(),
            data_for_method={},
        )
        LOG.info('Initializing repository successfull complete')

    def __dump_database(
        self,
    ) -> str:
        """Dump the PostgreSQL database to a string.

        Executes a command to generate a database dump.

        Returns:
            str: The database dump content as a string.

        Raises:
            ExecuteError: If the dump command fails.
            OSError: If an OS-level error occurs.
        """
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
        """Write the database dump to a file and move it to the storage dir.

        Args:
            dump (str): The database dump content as a string.

        Raises:
            ExecuteError: If the file write or move operation fails.
        """
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
        """Restore the PostgreSQL database from a backup file.

        This method drops the current database, recreates it, and populates it
        with data from the backup file.

        Raises:
            ExecuteError: If the restore command fails.
            OSError: If an OS-level error occurs.
        """
        backup_file = str(STORAGE_DATA / self.backup_file_name)
        db_name: str = db_config['db_name']
        db_user: str = db_config['user']
        with self.uow:
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
                    params=ExecuteParams(  # noqa: S604
                        shell=True, raise_on_error=False, run_as_root=True
                    ),
                )
            except (ExecuteError, OSError) as err:
                LOG.error(f'{err!s}')
                raise

            LOG.info(f'Database restored successfully from: {backup_file}')

    def __create_data_for_domain_manager(self) -> Dict[str, Any]:
        """Generate data for the domain layer manager.

        Returns:
            Dict[str, Any]: Data required to initialize or manage domain layer
                tasks.

        Raises:
            WrongBackuperTypeError: If the `BACKUPER_TYPE` configuration is
                invalid.
        """
        if BACKUPER_TYPE == 'restic':
            return DataForResticManager().model_dump()
        message = f'Unknown backuper type: {BACKUPER_TYPE}.'
        LOG.error(message)
        raise WrongBackuperTypeError(message)
