"""SNMP AgentX management.

This module defines the `SNMPAgentx` class, which manages the registration
and setup of various SNMP modules for monitoring CPU, RAM, disks, and network
interfaces.

Classes:
    SNMPAgentx: Manager class for setting up and registering SNMP modules.
"""

from typing import NoReturn

import pyagentx3 as pyagentx

from openvair.libs.log import get_logger
from openvair.modules.snmp.domain.base import BaseSNMP
from openvair.modules.snmp.domain.exceptions import (
    SNMPAgentStopError,
    SNMPAgentStartError,
    SNMPConnectionError,
    SNMPModuleRegistrationError,
)
from openvair.modules.snmp.domain.agentx.modules.cpu import Cpu
from openvair.modules.snmp.domain.agentx.modules.ram import Ram
from openvair.modules.snmp.domain.agentx.modules.disks import Disks
from openvair.modules.snmp.domain.agentx.modules.network import Networks

LOG = get_logger('domain-manager')
BASE_OID = '1.3.6.1.4.1.54641'
UPDATE_FREQ = 10


class SNMPAgentx(BaseSNMP, pyagentx.Agent):
    """Manager class for setting up and registering SNMP modules.

    This class manages the setup and registration of SNMP modules for
    monitoring system metrics like CPU, RAM, disks, and network interfaces.
    """

    def __init__(self) -> None:
        """Initialize the SNMPAgentx with logging setup."""
        super().__init__()
        try:
            pyagentx.Agent.__init__(self)
            pyagentx.setup_logging()
        except Exception as e:  # noqa: BLE001
            message = f'Failed to initialize SNMP agent: {e}'
            LOG.error(message)
            raise SNMPConnectionError(message)

    def setup(self) -> None:
        """Register SNMP modules for monitoring various system metrics."""
        LOG.info('Registering SNMP modules for monitoring')
        try:
            self.register(f'{BASE_OID}.50', Cpu, freq=UPDATE_FREQ)
            self.register(f'{BASE_OID}.51', Networks, freq=UPDATE_FREQ)
            self.register(f'{BASE_OID}.52', Disks, freq=UPDATE_FREQ)
            self.register(f'{BASE_OID}.53', Ram, freq=UPDATE_FREQ)
            LOG.info('All modules were registered successfully')
        except Exception as e:  # noqa: BLE001
            message = f'Failed to register modules: {e}'
            LOG.error(message)
            raise SNMPModuleRegistrationError(message)

    def start(self) -> NoReturn:  # type: ignore
        """Start the SNMP agent."""
        LOG.info('Starting SNMP agent')
        try:
            pyagentx.Agent.start(self)
            LOG.info('SNMP agent started successfully')
        except (SNMPModuleRegistrationError, Exception) as e:  # noqa: BLE001 cause may be unknown SNMP Exception
            message = f'Failed to start SNMP agent: {e}'
            raise SNMPAgentStartError(message)

    def stop(self) -> None:
        """Stop the SNMP agent."""
        LOG.info('Stopping SNMP agent')
        try:
            pyagentx.Agent.stop(self)
            LOG.info('SNMP agent stopped successfully')
        except Exception as e:  # noqa: BLE001
            msg = f'Failed to stop SNMP agent: {e}'
            raise SNMPAgentStopError(msg)
