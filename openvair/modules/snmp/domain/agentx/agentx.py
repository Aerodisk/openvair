"""SNMP AgentX management.

This module defines the `SNMPAgentx` class, which manages the registration
and setup of various SNMP modules for monitoring CPU, RAM, disks, and network
interfaces.

Classes:
    SNMPAgentx: Manager class for setting up and registering SNMP modules.
"""

import pyagentx3 as pyagentx

from openvair.libs.log import get_logger
from openvair.modules.snmp.domain.agentx.modules.cpu import Cpu
from openvair.modules.snmp.domain.agentx.modules.ram import Ram
from openvair.modules.snmp.domain.agentx.modules.disks import Disks
from openvair.modules.snmp.domain.agentx.modules.network import Networks

LOG = get_logger('domain-manager')


class SNMPAgentx(pyagentx.Agent):
    """Manager class for setting up and registering SNMP modules.

    This class manages the setup and registration of SNMP modules for
    monitoring system metrics like CPU, RAM, disks, and network interfaces.
    """

    def __init__(self):
        """Initialize the SNMPAgentx with logging setup."""
        super().__init__()
        pyagentx.setup_logging()

    def setup(self) -> None:
        """Register SNMP modules for monitoring various system metrics."""
        self.register('1.3.6.1.4.1.54641.50', Cpu, freq=10)
        self.register('1.3.6.1.4.1.54641.51', Networks, freq=10)
        self.register('1.3.6.1.4.1.54641.52', Disks, freq=10)
        self.register('1.3.6.1.4.1.54641.53', Ram, freq=10)
