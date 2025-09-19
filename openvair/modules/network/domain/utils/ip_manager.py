"""Network interface management.

This module provides classes and methods for managing network interfaces
using standard IP commands.

Classes:
    NetworkIPManager: Basic network interface manager designed to execute
        standard IP commands to manage network interfaces.
"""

from typing import Any

from openvair.libs.log import get_logger
from openvair.libs.cli.models import ExecuteParams
from openvair.libs.cli.executor import execute
from openvair.libs.data_handlers.json.serializer import deserialize_json
from openvair.modules.network.domain.utils.exceptions import (
    IPManagerException,
    InvalidAddressException,
)

LOG = get_logger(__name__)


class IPManager:
    """Basic network interface manager.

    Designed to execute standard IP commands to manage network interfaces.
    """

    def _get_addresses_data(self) -> dict[str, dict[str, Any]]:
        command = 'ip -j a'
        exec_res = execute(
            command,
            params=ExecuteParams(  # noqa: S604
                run_as_root=True,
                shell=True,
            ),
        )
        if exec_res.stderr:
            message = f'Failure while getting addresses info: {exec_res.stderr}'
            LOG.error(message)
            raise IPManagerException(message)
        addresses: list[dict] = deserialize_json(exec_res.stdout)
        return {iface['ifname']: iface for iface in addresses}

    def _get_interfaces_data(self) -> dict[str, dict[str, Any]]:
        command = 'ip -j link show'
        exec_res = execute(
            command,
            params=ExecuteParams(  # noqa: S604
                run_as_root=True,
                shell=True,
            ),
        )
        if exec_res.stderr:
            message = f'Failure while gettin interfaces info: {exec_res.stderr}'
            LOG.error(message)
            raise IPManagerException(message)
        interfaces: list[dict] = deserialize_json(exec_res.stdout)
        return {iface['ifname']: iface for iface in interfaces}

    def _get_routes_data(self) -> list[dict]:
        command = 'ip -j route'
        exec_res = execute(
            command,
            params=ExecuteParams(shell=True),  # noqa: S604
        )
        if exec_res.stderr:
            msg = f'Failure while getting main port name: {exec_res.stderr}'
            raise IPManagerException(msg)
        routes_info: list[dict] = deserialize_json(exec_res.stdout)
        return routes_info

    def get_iface_data(self, iface_name: str) -> dict:
        """Find and return data about interface by name"""
        interfaces = self._get_interfaces_data()
        interface: dict = interfaces.get(iface_name, {})
        if not interface:
            message = f'Interface data for {iface_name} not found'
            error = IPManagerException(message)
            LOG.error(error)
            raise error
        return interface

    def get_main_port_name(self) -> str:
        """Get the name of the main ethernet port (interface).

        Returns:
            str: The name of the main ethernet port.
        """
        routes_info = self._get_routes_data()

        main_port_name: str = ''
        for route_info in routes_info:
            if route_info.get('dst') == 'default':
                main_port_name = route_info.get('dev', '')
                LOG.info(f'Main port is: {main_port_name}')

        if not main_port_name:
            message = 'Main port(default) not found'
            error = IPManagerException(message)
            LOG.error(error)
            raise error

        return main_port_name

    @staticmethod
    def set_ip(iface_name: str, ip_address: str) -> str:
        """Set the IP address on the given interface.

        Args:
            iface_name (str): The name of the OVS interface.
            ip_address (str): The IP address to set.

        Returns:
            str: The output of the command.

        Raises:
            InvalidAddressException: If setting the IP address fails.
        """
        LOG.info(f'Setting IP: {ip_address} to the: {iface_name}')

        command = f'ip addr add {ip_address} dev {iface_name}'
        exec_res = execute(
            command,
            params=ExecuteParams(  # noqa: S604
                run_as_root=True,
                shell=True,
            ),
        )
        if exec_res.stderr:
            message = (
                f'Error setting IP address {ip_address} '
                f'for interface {iface_name}: {exec_res.stderr}'
            )
            raise InvalidAddressException(message)
        LOG.info(exec_res.stdout)
        LOG.info(exec_res.stderr)
        LOG.info('IP address was successfully set')
        return exec_res.stdout.strip()

    def set_alias(self, iface_name: str, alias: str) -> None:
        """Sertting alias for interface"""
        command = f'ip link set {iface_name} alias "{alias}"'
        exec_res = execute(
            command,
            params=ExecuteParams(  # noqa: S604
                run_as_root=True,
                shell=True,
            ),
        )
        if exec_res.stdout:
            message = (
                f'Error setting alias for interface {iface_name}: '
                f'{exec_res.stderr}'
            )
            err = IPManagerException(message)
            LOG.error(err)
            raise err

    @staticmethod
    def remove_interface_address(iface_name: str, ip_address: str) -> str:
        """Remove the given IP address from an OVS interface.

        Args:
            iface_name (str): The name of the OVS interface.
            ip_address (str): The IP address to remove.

        Returns:
            str: The output of the command.

        Raises:
            InvalidAddressException: If removing the IP address fails.
        """
        command = f'ip addr del {ip_address} dev {iface_name}'
        exec_res = execute(
            command,
            params=ExecuteParams(  # noqa: S604
                run_as_root=True,
                shell=True,
            ),
        )
        if exec_res.stderr:
            message = (
                f'Error removing IP address {ip_address} from interface '
                f'{iface_name}: {exec_res.stderr}'
            )
            raise InvalidAddressException(message)
        return exec_res.stdout.strip()

    @staticmethod
    def turn_on_interface(iface_name: str) -> str:
        """Turn on the given interface.

        Args:
            iface_name (str): The name of the interface.

        Returns:
            str: The output of the command.

        Raises:
            IPManagerException: If turning on the interface fails.
        """
        LOG.info('Turning the bridge on')
        command = f'ip link set {iface_name} up'
        exec_res = execute(
            command,
            params=ExecuteParams(  # noqa: S604
                run_as_root=True,
                shell=True,
            ),
        )
        if exec_res.stderr:
            message = (
                f'Error turning on interface {iface_name}: {exec_res.stderr}'
            )
            raise IPManagerException(message)
        LOG.info(f"The bridge '{iface_name}' was successfully created")

        return exec_res.stdout.strip()

    @staticmethod
    def turn_off_interface(iface_name: str) -> str:
        """Turn off the given interface.

        Args:
            iface_name (str): The name of the interface.

        Returns:
            str: The output of the command.

        Raises:
            IPManagerException: If turning off the interface fails.
        """
        command = f'ip link set {iface_name} down'
        exec_res = execute(
            command,
            params=ExecuteParams(  # noqa: S604
                run_as_root=True,
                shell=True,
            ),
        )
        if exec_res.stderr:
            message = (
                f'Error turning off interface {iface_name}: {exec_res.stderr}'
            )
            raise IPManagerException(message)
        return exec_res.stdout.strip()

    @staticmethod
    def check_interface_state(
        iface_name: str, expected_states: tuple = ('UP', 'DOWN', 'UNKNOW')
    ) -> bool:
        """Check the state of the given interface.

        Args:
            iface_name (str): The name of the interface.
            expected_states (set): List of expected states for the interface.

        Returns:
            bool: True if the interface has any of the expected states,
                False otherwise.
        """
        command = f'ip link show {iface_name}'
        exec_res = execute(
            command,
            params=ExecuteParams(  # noqa: S604
                run_as_root=True,
                shell=True,
            ),
        )
        if exec_res.stderr:
            message = (
                'Error occurred while checking interface state: '
                f'{exec_res.stderr}'
            )
            raise IPManagerException(message)
        return any(
            f'state {state}' in exec_res.stdout for state in expected_states
        )

    @staticmethod
    def get_interface_addresses(iface_name: str) -> list[str]:
        """Get the IP addresses assigned to the given interface name.

        Args:
            iface_name (str): The name of the interface.

        Returns:
            List[str]: A list of IP addresses assigned to the interface.

        Raises:
            NetworkInterfaceException: If retrieving the IP addresses fails.
        """
        command = (
            f'ip addr show {iface_name} | ' f"grep 'inet ' | awk '{{print $2}}'"
        )
        exec_res = execute(
            command,
            params=ExecuteParams(  # noqa: S604
                run_as_root=True,
                shell=True,
            ),
        )

        if exec_res.stderr:
            message = (
                f"Error occurred while getting interface '{iface_name}'"
                f' IP addresses: {exec_res.stderr}'
            )
            raise IPManagerException(message)

        return exec_res.stdout.strip().split('\n')

    # need replce by get_addresses
    @staticmethod
    def get_iface_ip(port_name: str) -> str:
        """Get a port's IP address.

        Args:
            port_name (str): The name of the port.

        Returns:
            str: The IP address of the port.

        Raises:
            NetworkInterfaceException: If retrieving the IP address fails.
        """
        command = (
            f'ip addr show {port_name} |'
            " awk '/inet / {print $2}' | cut -d '/' -f 1"
        )
        exec_res = execute(
            command,
            params=ExecuteParams(  # noqa: S604
                run_as_root=True,
                shell=True,
            ),
        )

        if exec_res.stderr:
            message = f'Failure while getting main port IP: {exec_res.stderr}'
            raise IPManagerException(message)

        if not exec_res.stdout.strip():
            LOG.info('Got an empty result while getting main port IP')
            return ''

        return exec_res.stdout.strip().split()[0]

    @staticmethod
    def flush_iface_ip(iface_name: str) -> str:
        """Remove all IP addresses from the given port.

        Args:
            iface_name (str): The name of the port to remove IP from.

        Returns:
            str: Command stdout.

        Raises:
            NetworkInterfaceException: If flushing the IP addresses fails.
        """
        LOG.info(f'Flushing IP from: {iface_name}...')
        command = f' ip addr flush dev {iface_name}'
        exec_res = execute(
            command,
            params=ExecuteParams(  # noqa: S604
                run_as_root=True,
                shell=True,
            ),
        )

        if exec_res.stderr:
            message = f'Failure while removing IP from port: {exec_res.stderr}'
            raise IPManagerException(message)

        return exec_res.stdout.strip()

    def is_dhcp_ip(self, iface_name: str) -> bool:
        """Check if dhcp enabled for interface"""
        LOG.info(f'Checking dhcp4 is enabled for {iface_name}...')
        routes = self._get_routes_data()
        for route in routes:
            if route['dev'] == iface_name and route['protocol'] == 'dhcp':
                LOG.info(f'dchp4 for {iface_name} is enable')
                return True

        LOG.info(f'dhcp4 for {iface_name} is disable')
        return False

    @staticmethod
    def run_dhclient(iface_name: str) -> str:
        """Run the DHCP client.

        Args:
            iface_name (str): Interface name.

        Returns:
            str: Command stdout.
        """
        command = f'dhclient {iface_name}'
        exec_res = execute(
            command,
            params=ExecuteParams(  # noqa: S604
                run_as_root=True,
                shell=True,
            ),
        )
        return exec_res.stdout.strip()

    def get_default_gateway_ip(self) -> str:
        """Get the default gateway IP for the given interface IP.

        Args:
            iface_ip (str): The interface IP.

        Returns:
            str: The gateway IP address.
        """
        LOG.info('Searching for default route')
        routes = self._get_routes_data()
        default_routes: list[dict[str, Any]] = list(
            filter(lambda x: x.get('dst') == 'default', routes)
        )
        addresses: tuple = tuple(dr.get('gateway') for dr in default_routes)

        self._check_defaoult_gateways(addresses)
        LOG.info(f'Default route is: {addresses[0]}')
        return str(addresses[0])

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
        LOG.info(f'Setting default gateway: {gateway_ip}')
        command = f'ip route add default via {gateway_ip}'
        exec_res = execute(
            command,
            params=ExecuteParams(  # noqa: S604
                run_as_root=True,
                shell=True,
            ),
        )

        if exec_res.stderr:
            message = (
                f'Failure while setting default gateway: {exec_res.stderr}'
            )
            raise IPManagerException(message)

        return exec_res.stdout.strip()

    def get_json_ifaces(self) -> dict:
        """Get network interfaces in JSON format.

        This method retrieves the list of network interfaces using the IP
        commandand returns it as a Dict.

        Returns:
            Dict: JSON object representing network interfaces.

        Raises:
            IPManagerException: If retrieving the network interfaces fails.
        """
        command = 'ip -j link show'
        exec_res = execute(
            command,
            params=ExecuteParams(shell=True),  # noqa: S604
        )

        if exec_res.stderr:
            message = exec_res.stderr
            raise IPManagerException(message)

        # Convert results of commands into dict
        ifaces: dict = deserialize_json(exec_res.stdout)
        return ifaces

    def _check_defaoult_gateways(self, addresses: tuple) -> None:
        if len(addresses) == 1:
            return

        message = 'Default gateway not found'
        if len(addresses) > 1:
            message = 'Find more than one default gateway'
        else:
            message = 'Default gateway not found'
        error = IPManagerException(message)
        LOG.error(error)
        raise error
