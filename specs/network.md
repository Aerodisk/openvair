# Open vAIR contract: network

Архитектурный контракт модуля `network` для RDE-линтера.
Источник кода: `openvair/modules/network`.

Машиночитаемый контракт — блок ``rde`` ниже.

```rde
meta:
  source: openvair/modules/network
feature: network
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
    - name: Interface
      methods: []
    - name: InterfaceExtraSpec
      methods: []
    - name: NetworkSqlAlchemyRepository
      methods:
      - get_by_name
  domain:
    required_classes:
    - name: AbstractInterfaceFactory
      methods:
      - get_interface
    - name: BaseBridge
      methods:
      - create
      - delete
      - get_bridges_list
    - name: BaseInterface
      methods:
      - disable
      - enable
    - name: BaseOVSBridge
      methods:
      - create
      - delete
      - get_bridges_list
    - name: BridgeNotFoundException
      methods: []
    - name: IPManager
      methods:
      - check_interface_state
      - flush_iface_ip
      - get_default_gateway_ip
      - get_iface_data
      - get_iface_ip
      - get_interface_addresses
      - get_json_ifaces
      - get_main_port_name
      - is_dhcp_ip
      - remove_interface_address
      - run_dhclient
      - set_alias
      - set_default_gateway
      - set_ip
      - turn_off_interface
      - turn_on_interface
    - name: IPManagerException
      methods: []
    - name: InterfaceFactory
      methods:
      - get_interface
    - name: InterfaceNotFoundException
      methods: []
    - name: InvalidAddressException
      methods: []
    - name: NetplanConfigReadingException
      methods: []
    - name: NetplanFileNotFoundException
      methods: []
    - name: NetplanInterface
      methods:
      - create
      - delete
    - name: NetplanManager
      methods:
      - apply
      - backup_iface_yaml
      - change_iface_yaml_file
      - create_iface_yaml
      - create_ovs_bridge_yaml_file
      - delete_iface_yaml
      - get_bkp_path_yaml
      - get_bridge_data_from_yaml
      - get_iface_data_from_yaml
      - get_path_yaml
      - rename_file_as_main_port
      - restore_backup_file
    - name: NoYAMLContentFoundFromNetplanGetError
      methods: []
    - name: OVSInterface
      methods:
      - create
      - delete
    - name: OVSManager
      methods:
      - add_interface
      - create_bridge
      - delete_bridge
      - get_bridges
      - get_ports_in_bridge
    - name: OVSManagerException
      methods: []
    - name: PhysicalInterface
      methods:
      - disable
      - enable
    - name: VirtualInterface
      methods:
      - disable
      - enable
    - name: YamlParsinError
      methods: []
  entrypoints:
    required_classes:
    - name: BridgeCreate
      methods: []
    - name: BridgeCreateResponse
      methods: []
    - name: Interface
      methods: []
    - name: InterfaceCrud
      methods:
      - create_bridge
      - delete_bridge
      - get_all_interfaces
      - get_bridges_list
      - get_interface
      - turn_off_interface
      - turn_on_interface
    - name: InterfaceExtraSpecs
      methods: []
    - name: ListOfInterfaces
      methods: []
    required_module_functions:
    - relative_path: entrypoints/api.py
      functions:
      - bridge_create
      - bridge_delete
      - get_bridges_list
      - get_interface
      - get_interfaces
      - turn_off_interface
      - turn_on_interface
    required_http_endpoints:
    - method: GET
      path: /interfaces/
      handler: get_interfaces
      parameters:
      - name: crud
        kind: depends
        required: true
        type_hint: InterfaceCrud
      - name: is_need_filter
        kind: query
        required: false
        type_hint: bool
    - method: GET
      path: /interfaces/bridges/
      handler: get_bridges_list
      parameters:
      - name: crud
        kind: depends
        required: true
        type_hint: InterfaceCrud
    - method: POST
      path: /interfaces/create/
      handler: bridge_create
      parameters:
      - name: crud
        kind: depends
        required: true
        type_hint: InterfaceCrud
      - name: data
        kind: body
        required: true
        type_hint: schemas.BridgeCreate
      - name: user_info
        kind: depends
        required: true
        type_hint: Dict
    - method: DELETE
      path: /interfaces/delete/
      handler: bridge_delete
      parameters:
      - name: crud
        kind: depends
        required: true
        type_hint: InterfaceCrud
      - name: data
        kind: query
        required: true
        type_hint: List[str]
      - name: user_info
        kind: depends
        required: true
        type_hint: Dict
    - method: GET
      path: /interfaces/{iface_id}/
      handler: get_interface
      parameters:
      - name: crud
        kind: depends
        required: true
        type_hint: InterfaceCrud
      - name: iface_id
        kind: query
        required: true
        type_hint: UUID
    - method: PUT
      path: /interfaces/{name}/turn_off
      handler: turn_off_interface
      parameters:
      - name: crud
        kind: depends
        required: true
        type_hint: InterfaceCrud
      - name: name
        kind: query
        required: true
        type_hint: str
    - method: PUT
      path: /interfaces/{name}/turn_on
      handler: turn_on_interface
      parameters:
      - name: crud
        kind: depends
        required: true
        type_hint: InterfaceCrud
      - name: name
        kind: query
        required: true
        type_hint: str
  service_layer:
    required_classes:
    - name: BridgeNameDoesNotExistException
      methods: []
    - name: BridgeNameExistException
      methods: []
    - name: CreateInterfaceDataException
      methods: []
    - name: InterfaceAlreadyExistException
      methods: []
    - name: InterfaceDeletingError
      methods: []
    - name: InterfaceInsertionError
      methods: []
    - name: InterfaceNotFoundError
      methods: []
    - name: InterfaceStatus
      methods: []
    - name: NestedOVSBridgeNotAllowedError
      methods: []
    - name: NetplanApplyException
      methods: []
    - name: NetworkServiceLayerManager
      methods:
      - create_bridge
      - delete_bridge
      - get_all_interfaces
      - get_bridges_list
      - get_interface
      - monitoring
      - turn_off
      - turn_on
    - name: NetworkSqlAlchemyUnitOfWork
      methods: []
    - name: UnexpectedDataArguments
      methods: []
```
