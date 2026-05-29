# Open vAIR contract: virtual_network

Архитектурный контракт модуля `virtual_network` для RDE-линтера.
Источник кода: `openvair/modules/virtual_network`.

Машиночитаемый контракт — блок ``rde`` ниже.

```rde
meta:
  source: openvair/modules/virtual_network
feature: virtual_network
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
    - name: PortGroup
      methods: []
    - name: VirtualNetwork
      methods: []
    - name: VirtualNetworkSqlAlchemyRepository
      methods:
      - get_by_name
  domain:
    required_classes:
    - name: AbstractVirtualNetworkFactory
      methods:
      - get_interface
    - name: BasePortGroup
      methods:
      - add_tag
      - as_dict
      - delete_tag
    - name: BaseVirtualNetwork
      methods:
      - add_port_group
      - add_tag_to_port_group
      - as_dict
      - create
      - del_port_group_by_name
      - delete
      - disable
      - enable
      - is_exist_in_virsh
    - name: BridgeNetwork
      methods:
      - add_port_group
      - add_tag_to_port_group
      - create
      - del_port_group_by_name
      - delete
      - disable
      - enable
      - is_exist_in_virsh
    - name: BridgePortGroup
      methods:
      - add_tag
      - delete_tag
    - name: PortGroupException
      methods: []
    - name: VirshDefineNetworkException
      methods: []
    - name: VirtualNetworkFactory
      methods:
      - get_interface
  entrypoints:
    required_classes:
    - name: ErrorResponseModel
      methods: []
    - name: ListOfVirtualNetworksResponse
      methods: []
    - name: PortGroup
      methods:
      - check_tags_and_is_trunk
    - name: VirtualNetwork
      methods:
      - bridge_validator
      - port_groups_validator
    - name: VirtualNetworkCrud
      methods:
      - add_port_group
      - add_tag_to_trunk_port_group
      - create_virtual_network
      - delete_port_group
      - delete_virtual_network
      - get_all_virtual_networks
      - get_virtual_network_by_id
      - get_virtual_network_by_name
      - turn_off_virtual_network
      - turn_on_virtual_network
    - name: VirtualNetworkResponse
      methods:
      - from_orm
    required_module_functions:
    - relative_path: entrypoints/api.py
      functions:
      - add_port_group
      - add_tag_to_trunk_port_group
      - create_virtual_network
      - delete_port_group
      - delete_virtual_network
      - get_virtual_network_by_id
      - get_virtual_network_by_name
      - get_virtual_networks
      - turn_off_virtual_network
      - turn_on_virtual_network
    required_http_endpoints:
    - method: GET
      path: /virtual_networks/
      handler: get_virtual_networks
      parameters:
      - name: crud
        kind: depends
        required: true
        type_hint: VirtualNetworkCrud
    - method: POST
      path: /virtual_networks/create/
      handler: create_virtual_network
      parameters:
      - name: crud
        kind: depends
        required: true
        type_hint: VirtualNetworkCrud
      - name: data
        kind: body
        required: true
        type_hint: schemas.VirtualNetwork
      - name: user_info
        kind: depends
        required: true
        type_hint: Dict
    - method: DELETE
      path: /virtual_networks/{virtual_network_id}
      handler: delete_virtual_network
      parameters:
      - name: crud
        kind: depends
        required: true
        type_hint: VirtualNetworkCrud
      - name: user_info
        kind: depends
        required: true
        type_hint: Dict
      - name: virtual_network_id
        kind: query
        required: true
        type_hint: UUID
    - method: GET
      path: /virtual_networks/{virtual_network_id}/
      handler: get_virtual_network_by_id
      parameters:
      - name: crud
        kind: depends
        required: true
        type_hint: VirtualNetworkCrud
      - name: virtual_network_id
        kind: query
        required: true
        type_hint: UUID
    - method: POST
      path: /virtual_networks/{virtual_network_id}/add_port_group
      handler: add_port_group
      parameters:
      - name: crud
        kind: depends
        required: true
        type_hint: VirtualNetworkCrud
      - name: port_group
        kind: body
        required: true
        type_hint: schemas.PortGroup
      - name: user_info
        kind: depends
        required: true
        type_hint: Dict
      - name: virtual_network_id
        kind: query
        required: true
        type_hint: str
    - method: DELETE
      path: /virtual_networks/{virtual_network_id}/delete_port_group
      handler: delete_port_group
      parameters:
      - name: crud
        kind: depends
        required: true
        type_hint: VirtualNetworkCrud
      - name: port_group_name
        kind: query
        required: true
        type_hint: str
      - name: user_info
        kind: depends
        required: true
        type_hint: Dict
      - name: virtual_network_id
        kind: query
        required: true
        type_hint: str
    - method: PUT
      path: /virtual_networks/{virtual_network_id}/turn_off
      handler: turn_off_virtual_network
      parameters:
      - name: crud
        kind: depends
        required: true
        type_hint: VirtualNetworkCrud
      - name: virtual_network_id
        kind: query
        required: true
        type_hint: str
    - method: PUT
      path: /virtual_networks/{virtual_network_id}/turn_on
      handler: turn_on_virtual_network
      parameters:
      - name: crud
        kind: depends
        required: true
        type_hint: VirtualNetworkCrud
      - name: virtual_network_id
        kind: query
        required: true
        type_hint: str
    - method: POST
      path: /virtual_networks/{virtual_network_id}/{port_group_name}/{trunk_id}/add_tag_id
      handler: add_tag_to_trunk_port_group
      parameters:
      - name: crud
        kind: depends
        required: true
        type_hint: VirtualNetworkCrud
      - name: port_group_name
        kind: query
        required: true
        type_hint: str
      - name: tag_id
        kind: query
        required: true
        type_hint: str
      - name: user_info
        kind: depends
        required: true
        type_hint: Dict
      - name: virtual_network_id
        kind: query
        required: true
        type_hint: str
    - method: GET
      path: /virtual_networks/{virtual_network_name}
      handler: get_virtual_network_by_name
      parameters:
      - name: crud
        kind: depends
        required: true
        type_hint: VirtualNetworkCrud
      - name: virtual_network_name
        kind: query
        required: true
        type_hint: str
  service_layer:
    required_classes:
    - name: DataBaseVirtualNetworkException
      methods: []
    - name: PortGroupException
      methods: []
    - name: VirtualNetworkAlreadyExist
      methods: []
    - name: VirtualNetworkDoesNotExist
      methods: []
    - name: VirtualNetworkServiceLayerManager
      methods:
      - add_port_group
      - add_tag_to_port_group
      - create_virtual_network
      - delete_port_group
      - delete_virtual_network
      - get_all_virtual_networks
      - get_virtual_network_by_id
      - get_virtual_network_by_name
      - monitoring
      - turn_off_virtual_network
      - turn_on_virtual_network
    - name: VirtualNetworkSqlAlchemyUnitOfWork
      methods: []
```
