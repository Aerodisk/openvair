# Open vAIR contract: backup

Архитектурный контракт модуля `backup` для RDE-линтера.
Источник кода: `openvair/modules/backup`.

Машиночитаемый контракт — блок ``rde`` ниже.

```rde
meta:
  source: openvair/modules/backup
feature: backup
layers:
  adapters:
    required_classes:
    - name: BackupSqlAlchemyRepository
      methods:
      - create_db
      - drop_db
      - terminate_all_connections
    - name: ResticAdapter
      methods:
      - backup
      - forget
      - init_repository
      - restore
      - snapshots
    - name: ResticBackupError
      methods: []
    - name: ResticCommandExecutor
      methods:
      - execute
    - name: ResticError
      methods: []
    - name: ResticExecutorError
      methods: []
    - name: ResticInitRepoError
      methods: []
    - name: ResticRestoreError
      methods: []
    - name: ReturnCode
      methods:
      - from_code
  domain:
    required_classes:
    - name: AbstractBackuperFactory
      methods:
      - get_backuper
    - name: BackupResticBackuperError
      methods: []
    - name: BackuperFactory
      methods:
      - get_backuper
    - name: BaseBackuper
      methods:
      - backup
      - restore
    - name: BaseBackuperError
      methods: []
    - name: FSBackuper
      methods:
      - delete_snapshot
      - get_snapshots
      - init_repository
    - name: InitRepositoryResticBackuperError
      methods: []
    - name: ResticBackuper
      methods:
      - backup
      - delete_snapshot
      - get_snapshots
      - init_repository
      - restore
    - name: RestoreResticBackuperError
      methods: []
    - name: SnapshotGettingResticBackuperError
      methods: []
  entrypoints:
    required_classes:
    - name: BackupCrud
      methods:
      - create_backup
      - delete_snapshot
      - get_snapshots
      - initialize_backup_repository
      - restore_backup
    required_module_functions:
    - relative_path: entrypoints/api.py
      functions:
      - create_backup
      - delete_backup
      - get_backups
      - init_repository
      - restore
    required_http_endpoints:
    - method: GET
      path: /backup/
      handler: get_backups
      parameters:
      - name: crud
        kind: depends
        required: true
        type_hint: BackupCrud
    - method: POST
      path: /backup/
      handler: create_backup
      parameters:
      - name: crud
        kind: depends
        required: true
        type_hint: BackupCrud
    - method: POST
      path: /backup/repository
      handler: init_repository
      parameters:
      - name: crud
        kind: depends
        required: true
        type_hint: BackupCrud
    - method: POST
      path: /backup/restore
      handler: restore
      parameters:
      - name: crud
        kind: depends
        required: true
        type_hint: BackupCrud
      - name: snapshot_id
        kind: query
        required: false
        type_hint: str
    - method: DELETE
      path: /backup/{snapshot_id}
      handler: delete_backup
      parameters:
      - name: crud
        kind: depends
        required: true
        type_hint: BackupCrud
      - name: snapshot_id
        kind: query
        required: true
        type_hint: str
  service_layer:
    required_classes:
    - name: BackupServiceLayerException
      methods: []
    - name: BackupServiceLayerManager
      methods:
      - create_backup
      - delete_snapshot
      - get_snapshots
      - initialize_backup_repository
      - restore_backup
    - name: BackupSqlAlchemyUnitOfWork
      methods: []
    - name: WrongBackuperTypeError
      methods: []
```
