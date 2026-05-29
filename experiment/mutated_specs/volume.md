# Open vAIR contract (mutated benchmark): volume

Архитектурный контракт модуля `volume` для RDE-линтера.
Источник кода: `openvair/modules/volume`.

Машиночитаемый контракт — блок ``rde`` ниже.

```rde
meta:
  source: openvair/modules/volume
feature: volume
layers:
  adapters:
    required_classes:
    - name: ApiAttachmentModelDTO
      methods: []
    - name: ApiVolumeModelDTO
      methods: []
    - name: AttachmentWebSerializer
      methods: []
    - name: Base
      methods: []
    - name: CloneVolumeDomainCommandDTO
      methods: []
    - name: CreateVolumeFromTemplateDomainCommandDTO
      methods: []
    - name: CreateVolumeFromTemplateModelDTO
      methods: []
    - name: CreateVolumeFromTemplateServiceCommandDTO
      methods: []
    - name: DataSerializer
      methods:
      - to_db
      - to_domain
      - to_web
    - name: DomainVolumeManagerDTO
      methods: []
    - name: StorageModelDTO
      methods:
      - extract_mount_point
    - name: TemplateModelDTO
      methods: []
    - name: Volume
      methods: []
    - name: VolumeAttachVM
      methods: []
    - name: VolumeDomainSerializer
      methods: []
    - name: VolumeSqlAlchemyRepository
      methods:
      - bulk_update
      - get_all_by_storage
      - get_by_name_and_storage
    - name: VolumeWebSerializer
      methods: []
    - name: PhantomRde_volume_adapters_1
      methods:
      - run
    - name: PhantomRde_volume_adapters_2
      methods:
      - run
    - name: PhantomRde_volume_adapters_3
      methods:
      - run
  domain:
    required_classes:
    - name: AbstractVolumeFactory
      methods:
      - get_volume
    - name: BaseVolume
      methods:
      - attach_volume_info
      - clone
      - create
      - create_from_template
      - delete
      - extend
    - name: DeleteVolumeException
      methods: []
    - name: LocalFSVolume
      methods:
      - attach_volume_info
      - clone
      - create
      - create_from_template
      - delete
      - extend
    - name: NfsVolume
      methods:
      - attach_volume_info
      - clone
      - create
      - create_from_template
      - delete
      - extend
    - name: QemuImgCreateException
      methods: []
    - name: QemuImgExtendException
      methods: []
    - name: VolumeDoesNotExistOnStorage
      methods: []
    - name: VolumeFactory
      methods:
      - get_volume
  entrypoints:
    required_classes:
    - name: AttachVolume
      methods: []
    - name: AttachVolumeInfo
      methods: []
    - name: Attachment
      methods: []
    - name: CreateVolume
      methods: []
    - name: CreateVolumeFromTemplate
      methods: []
    - name: DetachVolume
      methods: []
    - name: EditVolume
      methods: []
    - name: ExtendVolume
      methods: []
    - name: Volume
      methods: []
    - name: VolumeCrud
      methods:
      - attach_volume
      - create_from_template
      - create_volume
      - delete_volume
      - detach_volume
      - edit_volume
      - extend_volume
      - get_all_volumes
      - get_volume
    required_module_functions:
    - relative_path: entrypoints/api.py
      functions:
      - attach_volume
      - create_from_template
      - create_volume
      - delete_volume
      - detach_volume
      - edit_volume
      - extend_volume
      - get_volume
      - get_volumes
    required_http_endpoints:
    - method: GET
      path: /volumes/
      handler: get_volumes
      parameters:
      - name: crud
        kind: depends
        required: true
        type_hint: VolumeCrud
      - name: free_volumes
        kind: query
        required: false
        type_hint: bool
      - name: storage_id
        kind: query
        required: false
        type_hint: Optional[UUID]
    - method: POST
      path: /volumes/create/
      handler: create_volume
      parameters:
      - name: crud
        kind: depends
        required: true
        type_hint: VolumeCrud
      - name: data
        kind: body
        required: true
        type_hint: schemas.CreateVolume
      - name: user_info
        kind: depends
        required: true
        type_hint: Dict
    - method: POST
      path: /volumes/from_template/
      handler: create_from_template
      parameters:
      - name: crud
        kind: depends
        required: true
        type_hint: VolumeCrud
      - name: data
        kind: body
        required: true
        type_hint: schemas.CreateVolumeFromTemplate
      - name: user_info
        kind: depends
        required: true
        type_hint: Dict
    - method: DELETE
      path: /volumes/{volume_id}/
      handler: delete_volume
      parameters:
      - name: crud
        kind: depends
        required: true
        type_hint: VolumeCrud
      - name: user_info
        kind: depends
        required: true
        type_hint: Dict
      - name: volume_id
        kind: query
        required: true
        type_hint: UUID
    - method: GET
      path: /volumes/{volume_id}/
      handler: get_volume
      parameters:
      - name: crud
        kind: depends
        required: true
        type_hint: VolumeCrud
      - name: volume_id
        kind: query
        required: true
        type_hint: UUID
    - method: POST
      path: /volumes/{volume_id}/attach/
      handler: attach_volume
      parameters:
      - name: crud
        kind: depends
        required: true
        type_hint: VolumeCrud
      - name: data
        kind: body
        required: true
        type_hint: schemas.AttachVolume
      - name: user_info
        kind: depends
        required: true
        type_hint: Dict
      - name: volume_id
        kind: query
        required: true
        type_hint: UUID
    - method: DELETE
      path: /volumes/{volume_id}/detach/
      handler: detach_volume
      parameters:
      - name: crud
        kind: depends
        required: true
        type_hint: VolumeCrud
      - name: detach_info
        kind: body
        required: true
        type_hint: schemas.DetachVolume
      - name: user_info
        kind: depends
        required: true
        type_hint: Dict
      - name: volume_id
        kind: query
        required: true
        type_hint: UUID
    - method: PUT
      path: /volumes/{volume_id}/edit/
      handler: edit_volume
      parameters:
      - name: crud
        kind: depends
        required: true
        type_hint: VolumeCrud
      - name: data
        kind: body
        required: true
        type_hint: schemas.EditVolume
      - name: user_info
        kind: depends
        required: true
        type_hint: Dict
      - name: volume_id
        kind: query
        required: true
        type_hint: UUID
    - method: POST
      path: /volumes/{volume_id}/extend/
      handler: extend_volume
      parameters:
      - name: crud
        kind: depends
        required: true
        type_hint: VolumeCrud
      - name: data
        kind: body
        required: true
        type_hint: schemas.ExtendVolume
      - name: user_info
        kind: depends
        required: true
        type_hint: Dict
      - name: volume_id
        kind: query
        required: true
        type_hint: UUID
  service_layer:
    required_classes:
    - name: CreateVolumeDataException
      methods: []
    - name: StorageNotFoundException
      methods: []
    - name: StorageUnavailableException
      methods: []
    - name: UnexpectedDataArguments
      methods: []
    - name: ValidateArgumentsError
      methods: []
    - name: VmPowerStateIsNotShutOffException
      methods: []
    - name: VolumeExistsOnStorageException
      methods: []
    - name: VolumeHasAttachmentError
      methods: []
    - name: VolumeHasNotStorage
      methods: []
    - name: VolumeNotFoundException
      methods: []
    - name: VolumeServiceLayerManager
      methods:
      - attach_volume
      - clone_volume
      - create_from_template
      - create_volume
      - delete_volume
      - detach_volume
      - edit_volume
      - extend_volume
      - get_all_volumes
      - get_volume
      - monitoring
    - name: VolumeSqlAlchemyUnitOfWork
      methods: []
    - name: VolumeStatus
      methods: []
    - name: VolumeStatusException
      methods: []
```
