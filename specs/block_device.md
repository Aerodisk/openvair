# Open vAIR contract: block_device

Архитектурный контракт модуля `block_device` для RDE-линтера.
Источник кода: `openvair/modules/block_device`.

Машиночитаемый контракт — блок ``rde`` ниже.

```rde
meta:
  source: openvair/modules/block_device
feature: block_device
layers:
  adapters:
    required_classes:
    - name: Base
      methods: []
    - name: BlockDeviceSqlAlchemyRepository
      methods:
      - get_by_ip
    - name: DataSerializer
      methods:
      - to_db
      - to_domain
      - to_web
    - name: ISCSIInterface
      methods: []
  domain:
    required_classes:
    - name: AbstractInterfaceFactory
      methods:
      - get_interface
    - name: BaseBlockInterface
      methods:
      - discovery
      - get_host_iqn
      - login
      - logout
    - name: BaseFibreChannel
      methods:
      - lip_scan
    - name: BaseFibreChannelInterface
      methods:
      - lip_scan
    - name: BaseISCSI
      methods:
      - discovery
      - get_host_iqn
      - login
      - logout
    - name: FibreChannelInterface
      methods:
      - lip_scan
    - name: ISCSIDiscoveryError
      methods: []
    - name: ISCSIGetIQNException
      methods: []
    - name: ISCSIInterface
      methods:
      - discovery
      - get_host_iqn
      - login
      - logout
    - name: ISCSIIqnNotFoundException
      methods: []
    - name: ISCSILoginError
      methods: []
    - name: ISCSILogoutError
      methods: []
    - name: InterfaceFactory
      methods:
      - get_interface
    - name: LipScanError
      methods: []
  entrypoints:
    required_classes:
    - name: IQN
      methods: []
    - name: Interface
      methods: []
    - name: InterfaceCrud
      methods:
      - get_host_iqn
      - get_sessions
      - lip_scan
      - login
      - logout
    - name: InterfaceDeleted
      methods: []
    - name: InterfaceLogin
      methods: []
    - name: Session
      methods: []
    required_module_functions:
    - relative_path: entrypoints/api.py
      functions:
      - get_host_iqn
      - get_sessions
      - lip_scan
      - login
      - logout
    required_http_endpoints:
    - method: GET
      path: /block-devices/get-iqn
      handler: get_host_iqn
      parameters:
      - name: crud
        kind: depends
        required: true
        type_hint: InterfaceCrud
    - method: GET
      path: /block-devices/lip_scan
      handler: lip_scan
      parameters:
      - name: crud
        kind: depends
        required: true
        type_hint: InterfaceCrud
    - method: POST
      path: /block-devices/login
      handler: login
      parameters:
      - name: crud
        kind: depends
        required: true
        type_hint: InterfaceCrud
      - name: data
        kind: body
        required: true
        type_hint: schemas.Interface
      - name: user_data
        kind: depends
        required: true
        type_hint: Dict
    - method: POST
      path: /block-devices/logout
      handler: logout
      parameters:
      - name: crud
        kind: depends
        required: true
        type_hint: InterfaceCrud
      - name: data
        kind: body
        required: true
        type_hint: schemas.InterfaceDeleted
      - name: user_data
        kind: depends
        required: true
        type_hint: Dict
    - method: GET
      path: /block-devices/sessions
      handler: get_sessions
      parameters:
      - name: crud
        kind: depends
        required: true
        type_hint: InterfaceCrud
  service_layer:
    required_classes:
    - name: BlockDeviceSqlAlchemyUnitOfWork
      methods: []
    - name: BlockDevicesServiceLayerManager
      methods:
      - get_all_sessions
      - get_host_iqn
      - lip_scan
      - login
      - logout
    - name: FibreChannelLipScanException
      methods: []
    - name: ISCSIInterfaceStatus
      methods: []
    - name: ISCSIIqnGetException
      methods: []
    - name: ISCSILoginException
      methods: []
    - name: ISCSILogoutException
      methods: []
```
