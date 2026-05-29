# Open vAIR contract: virtual_machines

Архитектурный контракт модуля `virtual_machines` для RDE-линтера.
Источник кода: `openvair/modules/virtual_machines`.

Машиночитаемый контракт — блок ``rde`` ниже.

```rde
meta:
  source: openvair/modules/virtual_machines
feature: virtual_machines
layers:
  adapters:
    required_classes:
    - name: Base
      methods: []
    - name: CpuInfo
      methods: []
    - name: DataSerializer
      methods:
      - snapshot_to_db
      - snapshot_to_web
      - to_db
      - to_domain
      - to_web
      - vm_to_web
    - name: Disk
      methods: []
    - name: Os
      methods: []
    - name: ProtocolGraphicInterface
      methods: []
    - name: RAM
      methods: []
    - name: SnapshotSqlAlchemyRepository
      methods:
      - get_all_by_vm
      - get_by_name
      - get_children
      - get_current
      - set_current
      - unset_current
    - name: Snapshots
      methods: []
    - name: VMSqlAlchemyRepository
      methods:
      - bulk_update_disks
      - bulk_update_virtual_interfaces
      - delete_disk
      - delete_virtual_interfaces
      - get_disk_by_id
    - name: VirtualInterface
      methods: []
    - name: VirtualMachines
      methods: []
  domain:
    required_classes:
    - name: AbstractVMDriverFactory
      methods:
      - get_vm_driver
    - name: BaseLibvirtDriver
      methods:
      - create_external_snapshot
      - create_internal_snapshot
      - create_snapshot
      - delete_external_snapshot
      - delete_internal_snapshot
      - delete_snapshot
      - render_domain
      - revert_external_snapshot
      - revert_internal_snapshot
      - revert_snapshot
      - start
      - turn_off
      - vnc
    - name: BaseVMDriver
      methods:
      - create_snapshot
      - delete_snapshot
      - revert_snapshot
      - start
      - turn_off
      - vnc
    - name: GraphicPortNotFoundInXmlException
      methods: []
    - name: GraphicTypeNotFoundInXmlException
      methods: []
    - name: LibvirtDriver
      methods:
      - create_internal_snapshot
      - delete_internal_snapshot
      - redefine_snapshots
      - revert_internal_snapshot
      - start
      - turn_off
      - vnc
    - name: SnapshotError
      methods: []
    - name: SnapshotXmlError
      methods: []
    - name: VMDriverFactory
      methods:
      - get_vm_driver
    - name: VNCSessionError
      methods: []
  entrypoints:
    required_classes:
    - name: AttachImage
      methods: []
    - name: AttachVolume
      methods: []
    - name: AutoCreateVolume
      methods: []
    - name: CloneVm
      methods: []
    - name: Cpu
      methods: []
    - name: CreateSnapshot
      methods: []
    - name: CreateVirtualMachine
      methods: []
    - name: CreateVmDisks
      methods: []
    - name: DetachDisk
      methods: []
    - name: DetachVirtualInterface
      methods: []
    - name: Disk
      methods: []
    - name: DiskInfo
      methods: []
    - name: EditDisk
      methods: []
    - name: EditVirtualInterface
      methods: []
    - name: EditVirtualInterfaces
      methods: []
    - name: EditVm
      methods: []
    - name: EditVmDisks
      methods: []
    - name: GraphicInterfaceBase
      methods: []
    - name: GraphicInterfaceInfo
      methods: []
    - name: ListOfSnapshots
      methods: []
    - name: ListOfVirtualMachines
      methods: []
    - name: Os
      methods: []
    - name: QOS
      methods: []
    - name: RAM
      methods: []
    - name: SnapshotInfo
      methods: []
    - name: VMCrud
      methods:
      - clone_vm
      - create_snapshot
      - create_vm
      - delete_snapshot
      - delete_vm
      - edit_vm
      - get_all_vms
      - get_snapshot
      - get_snapshots
      - get_vm
      - revert_snapshot
      - shut_off_vm
      - start_vm
      - vnc
    - name: VirtualInterface
      methods: []
    - name: VirtualInterfaceInfo
      methods: []
    - name: VirtualMachineInfo
      methods: []
    - name: Vnc
      methods: []
    required_module_functions:
    - relative_path: entrypoints/api.py
      functions:
      - clone_vm
      - create_snapshot
      - create_vm
      - delete_snapshot
      - delete_vm
      - edit_vm
      - get_snapshot
      - get_snapshots
      - get_vm
      - get_vms
      - revert_snapshot
      - shut_off_vm
      - start_vm
      - vnc_vm
    required_http_endpoints:
    - method: GET
      path: /virtual-machines/
      handler: get_vms
      parameters:
      - name: crud
        kind: depends
        required: true
        type_hint: VMCrud
    - method: POST
      path: /virtual-machines/create/
      handler: create_vm
      parameters:
      - name: crud
        kind: depends
        required: true
        type_hint: VMCrud
      - name: data
        kind: body
        required: true
        type_hint: schemas.CreateVirtualMachine
      - name: user_info
        kind: depends
        required: true
        type_hint: Dict
    - method: DELETE
      path: /virtual-machines/{vm_id}/
      handler: delete_vm
      parameters:
      - name: crud
        kind: depends
        required: true
        type_hint: VMCrud
      - name: user_info
        kind: depends
        required: true
        type_hint: Dict
      - name: vm_id
        kind: path
        required: true
        type_hint: UUID
    - method: GET
      path: /virtual-machines/{vm_id}/
      handler: get_vm
      parameters:
      - name: crud
        kind: depends
        required: true
        type_hint: VMCrud
      - name: vm_id
        kind: path
        required: true
        type_hint: UUID
    - method: POST
      path: /virtual-machines/{vm_id}/clone/
      handler: clone_vm
      parameters:
      - name: crud
        kind: depends
        required: true
        type_hint: VMCrud
      - name: data
        kind: body
        required: true
        type_hint: schemas.CloneVm
      - name: user_info
        kind: depends
        required: true
        type_hint: Dict
      - name: vm_id
        kind: path
        required: true
        type_hint: UUID
    - method: POST
      path: /virtual-machines/{vm_id}/edit/
      handler: edit_vm
      parameters:
      - name: crud
        kind: depends
        required: true
        type_hint: VMCrud
      - name: data
        kind: body
        required: true
        type_hint: schemas.EditVm
      - name: user_info
        kind: depends
        required: true
        type_hint: Dict
      - name: vm_id
        kind: path
        required: true
        type_hint: UUID
    - method: POST
      path: /virtual-machines/{vm_id}/shut-off/
      handler: shut_off_vm
      parameters:
      - name: crud
        kind: depends
        required: true
        type_hint: VMCrud
      - name: user_info
        kind: depends
        required: true
        type_hint: Dict
      - name: vm_id
        kind: path
        required: true
        type_hint: UUID
    - method: GET
      path: /virtual-machines/{vm_id}/snapshots/
      handler: get_snapshots
      parameters:
      - name: crud
        kind: depends
        required: true
        type_hint: VMCrud
      - name: user_info
        kind: depends
        required: true
        type_hint: Dict
      - name: vm_id
        kind: path
        required: true
        type_hint: UUID
    - method: POST
      path: /virtual-machines/{vm_id}/snapshots/
      handler: create_snapshot
      parameters:
      - name: crud
        kind: depends
        required: true
        type_hint: VMCrud
      - name: data
        kind: body
        required: true
        type_hint: schemas.CreateSnapshot
      - name: user_info
        kind: depends
        required: true
        type_hint: Dict
      - name: vm_id
        kind: path
        required: true
        type_hint: UUID
    - method: DELETE
      path: /virtual-machines/{vm_id}/snapshots/{snap_id}
      handler: delete_snapshot
      parameters:
      - name: crud
        kind: depends
        required: true
        type_hint: VMCrud
      - name: snap_id
        kind: path
        required: true
        type_hint: UUID
      - name: user_info
        kind: depends
        required: true
        type_hint: Dict
      - name: vm_id
        kind: path
        required: true
        type_hint: UUID
    - method: GET
      path: /virtual-machines/{vm_id}/snapshots/{snap_id}
      handler: get_snapshot
      parameters:
      - name: crud
        kind: depends
        required: true
        type_hint: VMCrud
      - name: snap_id
        kind: path
        required: true
        type_hint: UUID
      - name: user_info
        kind: depends
        required: true
        type_hint: Dict
      - name: vm_id
        kind: path
        required: true
        type_hint: UUID
    - method: POST
      path: /virtual-machines/{vm_id}/snapshots/{snap_id}/revert
      handler: revert_snapshot
      parameters:
      - name: crud
        kind: depends
        required: true
        type_hint: VMCrud
      - name: snap_id
        kind: path
        required: true
        type_hint: UUID
      - name: user_info
        kind: depends
        required: true
        type_hint: Dict
      - name: vm_id
        kind: path
        required: true
        type_hint: UUID
    - method: POST
      path: /virtual-machines/{vm_id}/start/
      handler: start_vm
      parameters:
      - name: crud
        kind: depends
        required: true
        type_hint: VMCrud
      - name: user_info
        kind: depends
        required: true
        type_hint: Dict
      - name: vm_id
        kind: path
        required: true
        type_hint: UUID
    - method: GET
      path: /virtual-machines/{vm_id}/vnc/
      handler: vnc_vm
      parameters:
      - name: crud
        kind: depends
        required: true
        type_hint: VMCrud
      - name: user_info
        kind: depends
        required: true
        type_hint: Dict
      - name: vm_id
        kind: path
        required: true
        type_hint: UUID
  service_layer:
    required_classes:
    - name: ComesEmptyVolumeInfo
      methods: []
    - name: CreateVMDataException
      methods: []
    - name: DiskType
      methods: []
    - name: DuplicateDiskException
      methods: []
    - name: MaxTriesError
      methods: []
    - name: SnapshotLimitExceeded
      methods: []
    - name: SnapshotNameExistsError
      methods: []
    - name: SnapshotNotFoundException
      methods: []
    - name: SnapshotStatus
      methods: []
    - name: SnapshotStatusException
      methods: []
    - name: UnexpectedDataArguments
      methods: []
    - name: VMNotFoundException
      methods: []
    - name: VMPowerStateException
      methods: []
    - name: VMServiceLayerManager
      methods:
      - clone_vm
      - create_snapshot
      - create_vm
      - delete_snapshot
      - delete_vm
      - edit_vm
      - get_all_vms
      - get_snapshot
      - get_snapshots
      - get_vm
      - monitoring
      - revert_snapshot
      - shut_off_vm
      - start_vm
      - vnc
    - name: VMSqlAlchemyUnitOfWork
      methods: []
    - name: VMStatusException
      methods: []
    - name: ValidateArgumentsError
      methods: []
    - name: VmPowerState
      methods: []
    - name: VmStatus
      methods: []
    - name: VolumeCloneException
      methods: []
    - name: VolumeStatusIsError
      methods: []
```
