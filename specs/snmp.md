# Open vAIR contract: snmp

Архитектурный контракт модуля `snmp` для RDE-линтера.
Источник кода: `openvair/modules/snmp`.

Машиночитаемый контракт — блок ``rde`` ниже.

```rde
meta:
  source: openvair/modules/snmp
feature: snmp
layers:
  domain:
    required_classes:
    - name: AbstractSNMPFactory
      methods:
      - get_snmp_agent
    - name: BaseSNMP
      methods:
      - setup
      - start
      - stop
    - name: Cpu
      methods:
      - update
    - name: Disks
      methods:
      - get_disks_data
      - update
    - name: Networks
      methods:
      - update
    - name: Ram
      methods:
      - update
    - name: SNMPAgentStartError
      methods: []
    - name: SNMPAgentStopError
      methods: []
    - name: SNMPAgentTypeError
      methods: []
    - name: SNMPAgentx
      methods:
      - setup
      - start
      - stop
    - name: SNMPConnectionError
      methods: []
    - name: SNMPFactory
      methods:
      - get_snmp_agent
    - name: SNMPModuleRegistrationError
      methods: []
    required_module_functions:
    - relative_path: domain/manager.py
      functions:
      - main
```
