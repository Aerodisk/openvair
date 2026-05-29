# Open vAIR contract: dashboard

Архитектурный контракт модуля `dashboard` для RDE-линтера.
Источник кода: `openvair/modules/dashboard`.

Машиночитаемый контракт — блок ``rde`` ниже.

```rde
meta:
  source: openvair/modules/dashboard
feature: dashboard
layers:
  adapters:
    required_classes:
    - name: AbstractRepository
      methods:
      - get_data
    - name: PrometheusRepository
      methods: []
  entrypoints:
    required_classes:
    - name: BandWithData
      methods: []
    - name: CpuData
      methods: []
    - name: DashboardCrud
      methods:
      - get_data
    - name: DiskInfo
      methods: []
    - name: IOLatency
      methods: []
    - name: IopsData
      methods: []
    - name: MemoryData
      methods: []
    - name: NodeInfo
      methods: []
    - name: StoragesData
      methods: []
    required_module_functions:
    - relative_path: entrypoints/api.py
      functions:
      - get_node_data
    required_http_endpoints:
    - method: GET
      path: /dashboard/
      handler: get_node_data
      parameters:
      - name: crud
        kind: depends
        required: true
        type_hint: DashboardCrud
  service_layer:
    required_classes:
    - name: DashboardServiceLayerManager
      methods:
      - get_data
    - name: PrometheusUnitOfWork
      methods: []
```
