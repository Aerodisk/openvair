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
from openvair.modules.snmp.domain.model import SNMPFactory
from openvair.modules.snmp.domain.exceptions import SNMPAgenTypeError

LOG = get_logger('domain-manager')
SNMP_AGENT = get_snmp_agent()


def main() -> None:
    """Start the SNMP agent."""
    try:
        snmp_factory = SNMPFactory()
        agent = snmp_factory.get_snmp_agent(SNMP_AGENT)
        agent.start()
    except SNMPAgenTypeError as e:
        LOG.error(f'SNMP type error: {e}')
    except Exception as e:  # noqa: BLE001
        LOG.error(f'Unhandled exception: {e}')
        agent.stop()
    except KeyboardInterrupt:
        agent.stop()


if __name__ == '__main__':
    LOG.info("Starting SNMP agent with custom OID's on .54641")
    main()
