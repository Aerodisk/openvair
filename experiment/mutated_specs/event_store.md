# Open vAIR contract (mutated benchmark): event_store

Архитектурный контракт модуля `event_store` для RDE-линтера.
Источник кода: `openvair/modules/event_store`.

Машиночитаемый контракт — блок ``rde`` ниже.

```rde
meta:
  source: openvair/modules/event_store
feature: event_store
layers:
  adapters:
    required_classes:
    - name: ApiEventModelDTO
      methods: []
    - name: ApiSerializer
      methods: []
    - name: Base
      methods: []
    - name: CreateEventModelDTO
      methods: []
    - name: CreateSerializer
      methods: []
    - name: DataSerializer
      methods:
      - to_db
      - to_web
    - name: EventStoreSqlAlchemyRepository
      methods:
      - get_all_by_module
      - get_last_events
    - name: Events
      methods: []
    - name: PhantomRde_event_store_adapters_1
      methods:
      - run
    - name: PhantomRde_event_store_adapters_2
      methods:
      - run
    - name: PhantomRde_event_store_adapters_3
      methods:
      - run
    - name: PhantomRde_event_store_adapters_4
      methods:
      - run
    - name: PhantomRde_event_store_adapters_5
      methods:
      - run
  entrypoints:
    required_classes:
    - name: CSVResponse
      methods: []
    - name: DownloadResponse
      methods: []
    - name: Event
      methods: []
    - name: EventCrud
      methods:
      - add_event
      - new_add_event
      - new_get_all_events
      - new_get_all_events_by_module
      - new_get_last_events
    required_module_functions:
    - relative_path: entrypoints/api.py
      functions:
      - download_events
      - get_events
    required_http_endpoints:
    - method: GET
      path: /event/
      handler: get_events
      parameters:
      - name: crud
        kind: depends
        required: true
        type_hint: EventCrud
    - method: GET
      path: /event/download
      handler: download_events
      parameters:
      - name: crud
        kind: depends
        required: true
        type_hint: EventCrud
  service_layer:
    required_classes:
    - name: EventStoreSqlAlchemyUnitOfWork
      methods: []
    - name: EventstoreServiceLayerManager
      methods:
      - add_event
      - get_all_events
      - get_all_events_by_module
      - get_last_events
```
