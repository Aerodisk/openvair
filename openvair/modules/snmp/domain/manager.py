"""SNMP manager for starting the SNMP agent.

This module provides the main function for starting the SNMP agent with
custom OIDs. It supports both SNMPv2 and SNMPv3 with authentication and
encryption.

Usage:
    SNMPv3:
    - Create a user with a password:
        net-snmp-create-v3-user -ro -a 'P@ssw0rd' -x 'P@ssw0rd' -X DES testUserName

    - Example command:
        snmpwalk -v3 -u testUserName -l authPriv -a MD5 -A "P@ssw0rd" -x DES -X "P@ssw0rd" localhost 1.3.6.1.4.1.54641

    SNMPv2:
    - Example command:
        snmpwalk -v2c -c public localhost 1.3.6.1.4.1.54641
"""  # noqa: E501, W505 because commands need to be inline for correct usage

from openvair.libs.log import get_logger
from openvair.libs.client.config import get_snmp_agent
from openvair.modules.snmp.domain.base import BaseSNMP
from openvair.modules.snmp.domain.model import SNMPFactory
from openvair.modules.snmp.domain.exceptions import (
    SNMPAgentStopError,
    SNMPAgentTypeError,
    SNMPAgentStartError,
    SNMPConnectionError,
    SNMPModuleRegistrationError,
)

LOG = get_logger('domain-manager')
SNMP_AGENT = get_snmp_agent()


def _stop_agent(agent: BaseSNMP) -> None:
    try:
        LOG.info('Stopping SNMP agent')
        agent.stop()
        LOG.info('SNMP agent stopped successfully')
    except SNMPAgentStopError as e:
        LOG.error(f'Failed to stop SNMP agent gracefully: {e}')
        raise


def main() -> None:
    """Start the SNMP agent.

    The function handles the lifecycle of the SNMP agent:
    1. Creates an agent instance using the factory
    2. Starts the agent and registers all modules
    3. Handles graceful shutdown on errors or interrupts

    Raises:
        SNMPAgentTypeError: When specified agent type is not supported
        SNMPConnectionError: When agent fails to establish connection
        SNMPModuleRegistrationError: When module registration fails
        SNMPAgentStartError: When agent fails to start
        SNMPAgentStopError: When agent fails to stop gracefully
    """
    try:
        LOG.info('Initializing SNMP agent factory')
        snmp_factory = SNMPFactory()
        LOG.info(f'Creating SNMP agent of type: {SNMP_AGENT}')
        agent: BaseSNMP = snmp_factory.get_snmp_agent(SNMP_AGENT)
    except SNMPAgentTypeError as err:
        LOG.error(f'SNMP type error: {err}')
        raise

    try:
        LOG.info('Starting SNMP agent')
        agent.start()

        LOG.info('SNMP agent started successfully')
    except (
        SNMPConnectionError,
        SNMPModuleRegistrationError,
        SNMPAgentStartError,
    ) as err:
        LOG.error(f'SNMP agent error: {err}')
        _stop_agent(agent)
    except KeyboardInterrupt:
        LOG.info('Received keyboard interrupt, initiating graceful shutdown')
        _stop_agent(agent)
    except Exception as err:  # noqa: BLE001
        LOG.error(f'Unexpected error occurred: {err}')
        _stop_agent(agent)


if __name__ == '__main__':
    LOG.info("Starting SNMP agent with custom OID's on .54641")
    main()
