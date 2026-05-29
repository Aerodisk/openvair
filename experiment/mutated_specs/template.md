# Open vAIR contract (mutated benchmark): template

Архитектурный контракт модуля `template` для RDE-линтера.
Источник кода: `openvair/modules/template`.

Машиночитаемый контракт — блок ``rde`` ниже.

```rde
meta:
  source: openvair/modules/template
feature: template
layers:
  adapters:
    required_classes:
    - name: ApiSerializer
      methods: []
    - name: ApiTemplateModelDTO
      methods: []
    - name: AsyncCreateTemplateServiceCommandDTO
      methods: []
    - name: Base
      methods: []
    - name: CreateSerializer
      methods: []
    - name: CreateTemplateDomainCommandDTO
      methods: []
    - name: CreateTemplateModelDTO
      methods: []
    - name: CreateTemplateServiceCommandDTO
      methods: []
    - name: DeleteTemplateServiceCommandDTO
      methods: []
    - name: DomainSerializer
      methods: []
    - name: DomainTemplateModelDTO
      methods: []
    - name: EditTemplateDomainCommandDTO
      methods: []
    - name: EditTemplateServiceCommandDTO
      methods: []
    - name: GetStorageCommandDTO
      methods: []
    - name: GetTemplateServiceCommandDTO
      methods: []
    - name: GetVmCommandDTO
      methods: []
    - name: GetVolumeCommandDTO
      methods: []
    - name: StorageModelDTO
      methods:
      - extract_mount_point
    - name: Template
      methods: []
    - name: TemplateNotFoundInDBException
      methods: []
    - name: TemplateSqlAlchemyRepository
      methods:
      - get_by_name
    - name: VMModelDTO
      methods: []
    - name: VolumeAttachment
      methods: []
    - name: VolumeModelDTO
      methods: []
    - name: PhantomRde_template_adapters_1
      methods:
      - run
    - name: PhantomRde_template_adapters_2
      methods:
      - run
    - name: PhantomRde_template_adapters_3
      methods:
      - run
    - name: PhantomRde_template_adapters_4
      methods:
      - run
    - name: PhantomRde_template_adapters_5
      methods:
      - run
  domain:
    required_classes:
    - name: AbstractTemplateFactory
      methods:
      - get_template
    - name: BaseTemplate
      methods:
      - create
      - delete
      - edit
      - ensure_not_in_use
    - name: Qcow2Template
      methods:
      - create
      - delete
      - edit
      - ensure_not_in_use
    - name: TemplateFactory
      methods:
      - get_template
    - name: TemplateFileCreatingException
      methods: []
    - name: TemplateFileDeletingException
      methods: []
    - name: TemplateFileEditingException
      methods: []
  entrypoints:
    required_classes:
    - name: RequestCreateTemplate
      methods: []
    - name: RequestEditTemplate
      methods: []
    - name: TemplateCrud
      methods:
      - create_template
      - delete_template
      - edit_template
      - get_all_templates
      - get_template
    - name: TemplateResponse
      methods: []
    required_module_functions:
    - relative_path: entrypoints/api.py
      functions:
      - create_template
      - delete_template
      - edit_template
      - get_template
      - get_templates
    required_http_endpoints:
    - method: GET
      path: /templates/
      handler: get_templates
      parameters:
      - name: crud
        kind: depends
        required: true
        type_hint: TemplateCrud
      - name: params
        kind: depends
        required: true
        type_hint: Params
    - method: POST
      path: /templates/
      handler: create_template
      parameters:
      - name: crud
        kind: depends
        required: true
        type_hint: TemplateCrud
      - name: data
        kind: query
        required: true
        type_hint: RequestCreateTemplate
    - method: DELETE
      path: /templates/{template_id}
      handler: delete_template
      parameters:
      - name: crud
        kind: depends
        required: true
        type_hint: TemplateCrud
      - name: template_id
        kind: query
        required: true
        type_hint: UUID
    - method: GET
      path: /templates/{template_id}
      handler: get_template
      parameters:
      - name: crud
        kind: depends
        required: true
        type_hint: TemplateCrud
      - name: template_id
        kind: query
        required: true
        type_hint: UUID
    - method: PATCH
      path: /templates/{template_id}
      handler: edit_template
      parameters:
      - name: crud
        kind: depends
        required: true
        type_hint: TemplateCrud
      - name: data
        kind: query
        required: true
        type_hint: RequestEditTemplate
      - name: template_id
        kind: query
        required: true
        type_hint: UUID
  service_layer:
    required_classes:
    - name: BaseVolumeAttachToActiveVmException
      methods: []
    - name: StorageRetrievalException
      methods: []
    - name: TemplateServiceLayerManager
      methods:
      - create_template
      - delete_template
      - edit_template
      - get_all_templates
      - get_template
    - name: TemplateSqlAlchemyUnitOfWork
      methods: []
    - name: VMRetrievalException
      methods: []
    - name: VolumeRetrievalException
      methods: []
```
