"""Network interface management.

This module provides classes and methods for managing network interfaces
using standard IP commands.

Classes:
    NetworkIPManager: Basic network interface manager designed to execute
        standard IP commands to manage network interfaces.
"""

from typing import List

from openvair.libs.log import get_logger
from openvair.modules.tools.utils import execute
from openvair.modules.network.domain.bridges.utils.exceptions import (
    InvalidAddressException,
    NetworkInterfaceException,
    NetworkIPManagerException,
    InterfaceNotFoundException,
)

LOG = get_logger(__name__)


class NetworkIPManager:
    """Basic network interface manager.

    Designed to execute standard IP commands to manage network interfaces.
    """

    def get_main_port_name(self) -> str:
        """Get the name of the main ethernet port (interface).

        Returns:
            str: The name of the main ethernet port.
        """
        try:
            cmd = (
                "ip link show | awk -F: '$0 !~ "
                '"lo|vir|wl|^[^0-9]"{print $2;getline}\''
            )
            result, error = execute(cmd)
            if error:
                msg = f'Failure while getting main port name: {error}'
                raise InterfaceNotFoundException(msg)

            main_port_name = result.strip().split()[0]
        except NetworkIPManagerException as err:
            LOG.error(err)
            raise

        return main_port_name

    @staticmethod
    def set_interface_address(interface_name: str, ip_address: str) -> str:
        """Set the IP address on the given interface.

        Args:
            interface_name (str): The name of the OVS interface.
            ip_address (str): The IP address to set.

        Returns:
            str: The output of the command.

        Raises:
            InvalidAddressException: If setting the IP address fails.
        """
        LOG.info(f'Got IP address: {ip_address}')
        command = f'sudo ip addr add {ip_address}/24 dev {interface_name}'
        result, error = execute(command)
        if error:
            msg = (
                f'Error setting IP address {ip_address} '
                f'for interface {interface_name}: {error}'
            )
            raise InvalidAddressException(msg)
        LOG.info('IP address was successfully set')
        return result.strip()

    @staticmethod
    def remove_interface_address(interface_name: str, ip_address: str) -> str:
        """Remove the given IP address from an OVS interface.

        Args:
            interface_name (str): The name of the OVS interface.
            ip_address (str): The IP address to remove.

        Returns:
            str: The output of the command.

        Raises:
            InvalidAddressException: If removing the IP address fails.
        """
        command = f'sudo ip addr del {ip_address} dev {interface_name}'
        result, error = execute(command)
        if error:
            msg = (
                f'Error removing IP address {ip_address} from interface '
                f'{interface_name}: {error}'
            )
            raise InvalidAddressException(msg)
        return result.strip()

    @staticmethod
    def turn_on_interface(interface_name: str) -> str:
        """Turn on the given interface.

        Args:
            interface_name (str): The name of the interface.

        Returns:
            str: The output of the command.

        Raises:
            NetworkInterfaceException: If turning on the interface fails.
        """
        LOG.info('Turning the bridge on')
        command = f'sudo ip link set {interface_name} up'
        result, error = execute(command)

        if error:
            msg = f'Error turning on interface {interface_name}: {error}'
            raise NetworkInterfaceException(msg)
        LOG.info(f"The bridge '{interface_name}' was successfully created")

        return result.strip()

    @staticmethod
    def turn_off_interface(interface_name: str) -> str:
        """Turn off the given interface.

        Args:
            interface_name (str): The name of the interface.

        Returns:
            str: The output of the command.

        Raises:
            NetworkInterfaceException: If turning off the interface fails.
        """
        command = f'sudo ip link set {interface_name} down'
        result, error = execute(command)
        if error:
            msg = f'Error turning off interface {interface_name}: {error}'
            raise NetworkInterfaceException(msg)
        return result.strip()

    @staticmethod
    def check_interface_state(
        interface_name: str, expected_states: tuple = ('UP', 'DOWN')
    ) -> bool:
        """Check the state of the given interface.

        Args:
            interface_name (str): The name of the interface.
            expected_states (set): List of expected states for the interface.

        Returns:
            bool: True if the interface has any of the expected states,
                  False otherwise.
        """
        command = f'sudo ip link show {interface_name}'
        result, error = execute(command)
        if error:
            msg = f'Error occurred while checking interface state: {error}'
            raise NetworkInterfaceException(msg)
        return any(f'state {state}' in result for state in expected_states)

    @staticmethod
    def get_interface_addresses(interface_name: str) -> List[str]:
        """Get the IP addresses assigned to the given interface name.

        Args:
            interface_name (str): The name of the interface.

        Returns:
            List[str]: A list of IP addresses assigned to the interface.

        Raises:
            NetworkInterfaceException: If retrieving the IP addresses fails.
        """
        command = (
            f'sudo ip addr show {interface_name} | '
            f"grep 'inet ' | awk '{{print $2}}'"
        )
        result, error = execute(command)

        if error:
            msg = (
                f"Error occurred while getting interface '{interface_name}'"
                f' IP addresses: {error}'
            )
            raise NetworkInterfaceException(msg)

        return result.strip().split('\n')

    @staticmethod
    def get_interface_ip_address(port_name: str) -> str:
        """Get a port's IP address.

        Args:
            port_name (str): The name of the port.

        Returns:
            str: The IP address of the port.

        Raises:
            NetworkInterfaceException: If retrieving the IP address fails.
        """
        command = (
            f'sudo ip addr show {port_name} |'
            " awk '/inet / {print $2}' | cut -d '/' -f 1"
        )
        result, error = execute(command)

        if error:
            msg = f'Failure while getting main port IP: {error}'
            raise NetworkInterfaceException(msg)

        if not result.strip():
            LOG.info('Got an empty result while getting main port IP')
            return ''

        return result.strip().split()[0]

    @staticmethod
    def flush_ip_from_interface(interface_name: str) -> str:
        """Remove all IP addresses from the given port.

        Args:
            interface_name (str): The name of the port to remove IP from.

        Returns:
            str: Command stdout.

        Raises:
            NetworkInterfaceException: If flushing the IP addresses fails.
        """
        command = f'sudo ip addr flush dev {interface_name}'
        result, error = execute(command)

        if error:
            msg = f'Failure while removing IP from port: {error}'
            raise NetworkInterfaceException(msg)

        return result.strip()

    @staticmethod
    def run_dhclient(interface_name: str) -> str:
        """Run the DHCP client.

        Args:
            interface_name (str): Interface name.

        Returns:
            str: Command stdout.
        """
        command = f'sudo dhclient {interface_name}'
        result, _ = execute(command)
        return result.strip()

    @staticmethod
    def get_default_gateway_ip(interface_ip: str) -> str:
        """Get the default gateway IP for the given interface IP.

        Args:
            interface_ip (str): The interface IP.

        Returns:
            str: The gateway IP address.
        """
        # TODO: add interface_ip validation
        return '.'.join(interface_ip.split('.')[:-1]) + '.1'

    @staticmethod
    def set_default_gateway(gateway_ip: str) -> str:
        """Set the default gateway using the provided IP.

        Args:
            gateway_ip (str): IP address of the default gateway.

        Returns:
            str: Command stdout.

        Raises:
            NetworkInterfaceException: If setting the default gateway fails.
        """
        command = f'sudo ip route add default via {gateway_ip}'
        result, error = execute(command)

        if error:
            msg = f'Failure while setting default gateway: {error}'
            raise NetworkInterfaceException(msg)

        return result.strip()
