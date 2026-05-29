# Open vAIR contract (mutated benchmark): storage

Архитектурный контракт модуля `storage` для RDE-линтера.
Источник кода: `openvair/modules/storage`.

Машиночитаемый контракт — блок ``rde`` ниже.

```rde
meta:
  source: openvair/modules/storage
feature: storage
layers:
  adapters:
    required_classes:
    - name: Base
      methods: []
    - name: DataSerializer
      methods:
      - to_db
      - to_domain
      - to_web
    - name: PartedAdapter
      methods:
      - mkpart
      - print
      - rm
    - name: PartedError
      methods: []
    - name: Storage
      methods: []
    - name: StorageExtraSpecs
      methods: []
    - name: StorageSqlAlchemyRepository
      methods:
      - bulk_update
      - filter_extra_specs
      - get_spec_by_key_value
      - get_storage_by_name
      - update_spec_by_key_for_storage
    - name: PhantomRde_storage_adapters_1
      methods:
      - run
    - name: PhantomRde_storage_adapters_2
      methods:
      - run
    - name: PhantomRde_storage_adapters_3
      methods:
      - run
    - name: PhantomRde_storage_adapters_4
      methods:
      - run
    - name: PhantomRde_storage_adapters_5
      methods:
      - run
  domain:
    required_classes:
    - name: AbstractStorageFactory
      methods:
      - get_storage
    - name: BasePartition
      methods:
      - create_partition
      - delete_partition
      - get_partitions_info
    - name: BaseStorage
      methods:
      - create
      - delete
      - do_setup
      - get_capacity_info
    - name: DiskSizeValueObject
      methods:
      - value_validator
    - name: GettinStorageInfoError
      methods: []
    - name: LocalDiskStorage
      methods:
      - do_setup
      - formatting
    - name: LocalFSStorage
      methods:
      - create
      - delete
      - do_setup
      - formatting
      - get_capacity_info
      - mount_point_name
      - mount_point_path
    - name: LocalPartition
      methods:
      - create_partition
      - delete_partition
      - get_partitions_info
    - name: NFSCantBeMountError
      methods: []
    - name: NfsIpIsNotAvailableError
      methods: []
    - name: NfsPathDoesNotExistOnShareError
      methods: []
    - name: NfsStorage
      methods:
      - do_setup
    - name: NotFoundDataInPartitonInfoException
      methods: []
    - name: PackageIsNotInstalled
      methods: []
    - name: PartedParser
      methods:
      - get_byte_value
      - parse_partitions_info
    - name: PartitionTableInfoNotFound
      methods: []
    - name: RemoteFSStorage
      methods:
      - create
      - delete
      - do_setup
      - get_capacity_info
      - mount_point_name
      - mount_point_path
    - name: StorageFactory
      methods:
      - get_storage
    - name: UnmountError
      methods: []
    - name: UnsupportedPartitionTableTypeError
      methods: []
    - name: WrongPartitionRangeError
      methods: []
  entrypoints:
    required_classes:
    - name: CreateLocalPartition
      methods: []
    - name: CreateStorage
      methods: []
    - name: DeleteLocalPartition
      methods: []
    - name: ListOfLocalDisks
      methods: []
    - name: LocalDisk
      methods: []
    - name: LocalFSStorageExtraSpecsCreate
      methods: []
    - name: LocalFSStorageExtraSpecsInfo
      methods: []
    - name: NfsStorageExtraSpecsCreate
      methods: []
    - name: NfsStorageExtraSpecsInfo
      methods: []
    - name: Storage
      methods: []
    - name: StorageCrud
      methods:
      - create_local_partition
      - create_storage
      - delete_local_partition
      - delete_storage
      - get_all_storages
      - get_local_disk_partitions_info
      - get_local_disks
      - get_storage
    required_module_functions:
    - relative_path: entrypoints/api.py
      functions:
      - create_local_partition
      - create_storage
      - delete_local_partition
      - delete_storage
      - get_local_disk_partitions_info
      - get_local_disks
      - get_storage
      - get_storages
    required_http_endpoints:
    - method: GET
      path: /storages/
      handler: get_storages
      parameters:
      - name: crud
        kind: depends
        required: true
        type_hint: StorageCrud
    - method: POST
      path: /storages/create/
      handler: create_storage
      parameters:
      - name: crud
        kind: depends
        required: true
        type_hint: StorageCrud
      - name: data
        kind: body
        required: true
        type_hint: schemas.CreateStorage
      - name: user_data
        kind: depends
        required: true
        type_hint: Dict
    - method: GET
      path: /storages/local-disks/
      handler: get_local_disks
      parameters:
      - name: crud
        kind: depends
        required: true
        type_hint: StorageCrud
      - name: free_local_disks
        kind: query
        required: false
        type_hint: Optional[bool]
    - method: POST
      path: /storages/local-disks/create_partition/
      handler: create_local_partition
      parameters:
      - name: crud
        kind: depends
        required: true
        type_hint: StorageCrud
      - name: data
        kind: body
        required: true
        type_hint: schemas.CreateLocalPartition
      - name: user_data
        kind: depends
        required: true
        type_hint: Dict
    - method: DELETE
      path: /storages/local-disks/delete_partition/
      handler: delete_local_partition
      parameters:
      - name: crud
        kind: depends
        required: true
        type_hint: StorageCrud
      - name: data
        kind: body
        required: true
        type_hint: schemas.DeleteLocalPartition
      - name: user_data
        kind: depends
        required: true
        type_hint: Dict
    - method: GET
      path: /storages/local-disks/partition_info/
      handler: get_local_disk_partitions_info
      parameters:
      - name: crud
        kind: depends
        required: true
        type_hint: StorageCrud
      - name: disk_path
        kind: query
        required: true
        type_hint: str
    - method: GET
      path: /storages/{storage_id}/
      handler: get_storage
      parameters:
      - name: crud
        kind: depends
        required: true
        type_hint: StorageCrud
      - name: storage_id
        kind: query
        required: true
        type_hint: UUID
    - method: DELETE
      path: /storages/{storage_id}/delete/
      handler: delete_storage
      parameters:
      - name: crud
        kind: depends
        required: true
        type_hint: StorageCrud
      - name: storage_id
        kind: query
        required: true
        type_hint: UUID
      - name: user_data
        kind: depends
        required: true
        type_hint: Dict
  service_layer:
    required_classes:
    - name: CannotCreateStorageOnRootOfSystemDisk
      methods: []
    - name: CannotCreateStorageOnSystemPartition
      methods: []
    - name: CannotDeleteSystemPartition
      methods: []
    - name: DeviceDoesNotExist
      methods: []
    - name: GetEmptyDomainStorageInfo
      methods: []
    - name: PartitionHasStorage
      methods: []
    - name: StorageAttributeError
      methods: []
    - name: StorageExistsError
      methods: []
    - name: StorageHasObjects
      methods: []
    - name: StorageNotFoundError
      methods: []
    - name: StorageServiceLayerManager
      methods:
      - create_local_partition
      - create_storage
      - delete_local_partition
      - delete_storage
      - get_all_storages
      - get_local_disk_partitions_info
      - get_local_disks
      - get_storage
      - monitoring
    - name: StorageSqlAlchemyUnitOfWork
      methods: []
    - name: StorageStatus
      methods: []
    - name: StorageStatusError
      methods: []
```
