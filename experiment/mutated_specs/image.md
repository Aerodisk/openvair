# Open vAIR contract (mutated benchmark): image

Архитектурный контракт модуля `image` для RDE-линтера.
Источник кода: `openvair/modules/image`.

Машиночитаемый контракт — блок ``rde`` ниже.

```rde
meta:
  source: openvair/modules/image
feature: image
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
    - name: Image
      methods: []
    - name: ImageAttachVM
      methods: []
    - name: ImageSqlAlchemyRepository
      methods:
      - bulk_update
      - get_all_by_storage
      - get_by_name
    - name: PhantomRde_image_adapters_1
      methods:
      - run
    - name: PhantomRde_image_adapters_2
      methods:
      - run
    - name: PhantomRde_image_adapters_3
      methods:
      - run
    - name: PhantomRde_image_adapters_4
      methods:
      - run
    - name: PhantomRde_image_adapters_5
      methods:
      - run
  domain:
    required_classes:
    - name: AbstractImageFactory
      methods:
      - get_image
    - name: BaseImage
      methods:
      - attach_image_info
      - delete
      - delete_from_tmp
      - upload
    - name: BaseLocalFSImage
      methods:
      - attach_image_info
      - delete
      - delete_from_tmp
      - upload
    - name: BaseRemoteFSImage
      methods:
      - attach_image_info
      - delete
      - delete_from_tmp
      - upload
    - name: ImageDoesNotExistOnStorage
      methods: []
    - name: ImageFactory
      methods:
      - get_image
    - name: LocalFSImage
      methods:
      - attach_image_info
      - delete
      - delete_from_tmp
      - upload
    - name: NfsImage
      methods:
      - attach_image_info
      - delete
      - delete_from_tmp
      - upload
  entrypoints:
    required_classes:
    - name: AttachImage
      methods: []
    - name: AttachImageInfo
      methods: []
    - name: Attachment
      methods: []
    - name: CreateImagePageException
      methods: []
    - name: DetachImage
      methods: []
    - name: FilenameLengthError
      methods: []
    - name: Image
      methods: []
    - name: ImageCrud
      methods:
      - attach_image
      - delete_image
      - detach_image
      - get_all_images
      - get_image
      - upload_image
    - name: NotSupportedExtensionError
      methods: []
    required_module_functions:
    - relative_path: entrypoints/api.py
      functions:
      - attach_image
      - delete_image
      - detach_image
      - get_image
      - get_images
      - upload_image
    required_http_endpoints:
    - method: GET
      path: /images/
      handler: get_images
      parameters:
      - name: crud
        kind: depends
        required: true
        type_hint: ImageCrud
      - name: storage_id
        kind: query
        required: false
        type_hint: Optional[UUID]
    - method: POST
      path: /images/upload/
      handler: upload_image
      parameters:
      - name: crud
        kind: depends
        required: true
        type_hint: ImageCrud
      - name: description
        kind: query
        required: false
        type_hint: str
      - name: image
        kind: body
        required: true
        type_hint: UploadFile
      - name: name
        kind: query
        required: true
        type_hint: str
      - name: storage_id
        kind: query
        required: true
        type_hint: UUID
      - name: user_info
        kind: depends
        required: true
        type_hint: Dict
    - method: DELETE
      path: /images/{image_id}/
      handler: delete_image
      parameters:
      - name: crud
        kind: depends
        required: true
        type_hint: ImageCrud
      - name: image_id
        kind: query
        required: true
        type_hint: UUID
      - name: user_info
        kind: depends
        required: true
        type_hint: Dict
    - method: GET
      path: /images/{image_id}/
      handler: get_image
      parameters:
      - name: crud
        kind: depends
        required: true
        type_hint: ImageCrud
      - name: image_id
        kind: query
        required: true
        type_hint: UUID
    - method: POST
      path: /images/{image_id}/attach/
      handler: attach_image
      parameters:
      - name: crud
        kind: depends
        required: true
        type_hint: ImageCrud
      - name: data
        kind: body
        required: true
        type_hint: schemas.AttachImage
      - name: image_id
        kind: query
        required: true
        type_hint: UUID
      - name: user_info
        kind: depends
        required: true
        type_hint: Dict
    - method: DELETE
      path: /images/{image_id}/detach/
      handler: detach_image
      parameters:
      - name: crud
        kind: depends
        required: true
        type_hint: ImageCrud
      - name: detach_info
        kind: body
        required: true
        type_hint: schemas.DetachImage
      - name: image_id
        kind: query
        required: true
        type_hint: UUID
      - name: user_info
        kind: depends
        required: true
        type_hint: Dict
  service_layer:
    required_classes:
    - name: ImageDeletingError
      methods: []
    - name: ImageHasAttachmentError
      methods: []
    - name: ImageHasNotStorage
      methods: []
    - name: ImageHasSameAttachment
      methods: []
    - name: ImageNameExistsException
      methods: []
    - name: ImageServiceLayerManager
      methods:
      - attach_image
      - delete_image
      - detach_image
      - get_all_images
      - get_image
      - monitoring
      - upload_image
    - name: ImageSqlAlchemyUnitOfWork
      methods: []
    - name: ImageStatus
      methods: []
    - name: ImageStatusError
      methods: []
    - name: ImageUnvailableError
      methods: []
    - name: StorageUnavailableException
      methods: []
    - name: UnexpectedDataArguments
      methods: []
    - name: UploadImageDataError
      methods: []
    - name: ValidateArgumentsError
      methods: []
```
