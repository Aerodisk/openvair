"""Module for managing and retrieving system network interfaces information.

This module provides classes and exceptions for handling network interface
data. It includes functionality to retrieve detailed information about
network interfaces, including physical and virtual properties, using system
utilities.

Classes:
    GettingSystemInfoError: Base exception for errors in system information
        retrieval.
    MissingRequiredComponentError: Exception raised when a required system
        component is missing.
    InterfacesFromSystem: Custom collection for storing and managing network
        interfaces data.
"""

import re
import json
from typing import Any, Dict, List, Optional

from openvair.libs.cli.models import ExecuteParams
from openvair.libs.cli.executor import execute
from openvair.abstracts.base_exception import BaseCustomException


class GettingSystemInfoError(BaseCustomException):
    """Raised for errors encountered during system information retrieval."""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize GettingSystemInfoError"""
        super().__init__(message, *args)


class MissingRequiredComponentError(GettingSystemInfoError):
    """Raised when a required system component, such as 'ip', is missing."""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize MissingRequiredComponentError"""
        super().__init__(message, *args)


class InterfacesFromSystem(list):
    """Custom collection of network interfaces data from system core."""

    def __init__(self) -> None:
        """Initialize the collection of network interfaces

        Retrieving all interface data from the system.
        """
        super().__init__(
            inf_data for inf_data in self._get_all_interfaces_data()
        )

    def _get_all_interfaces_data(self) -> List[Dict]:  # noqa: C901
        """Retrieve data for all network interfaces on the system.

        This method collects information about each network interface,
        distinguishing between physical and virtual interfaces, and gathering
        details such as IP, MAC address, duplex, and speed.

        Returns:
            List[Dict]: List of dictionaries containing data of all interfaces.

        Raises:
            MissingRequiredComponentError: If the 'ip' command is not available
                on the system.
            GettingSystemInfoError: If an error occurs during interface data
            retrieval.
        """
        all_interfaces_data = []

        exec_res = execute(
            'ip',
            '-json',
            'a',
            params=ExecuteParams(  # noqa: S604
                run_as_root=True,
                shell=True,
            ),
        )

        if exec_res.stderr == '/bin/sh: ip: command not found\n':
            message = (
                "Error in getting interfaces from system, cause util 'ip' not "
                'found.'
            )
            raise MissingRequiredComponentError(message)

        if exec_res.stderr != '':
            message = (
                f'Error in getting interfaces from system: {exec_res.stderr}'
            )
            raise GettingSystemInfoError(message)

        sys_output_infs: List[Dict] = json.loads(exec_res.stdout)

        for sys_inf in sys_output_infs:
            inf_data = {}
            inf_data['name'] = sys_inf.get('ifname', '')
            inf_data['mtu'] = sys_inf.get('mtu', '')
            inf_data['power_state'] = sys_inf.get('operstate', '')
            inf_data['mac'] = sys_inf.get('address', '')

            for param in sys_inf['addr_info']:
                if param['family'] == 'inet':
                    inf_data['ip'] = param['local']
                    inf_data['netmask'] = param['prefixlen']

            if sys_inf['ifname'] in self._get_physical_interfaces_list():
                inf_data['inf_type'] = 'physical'
                inf_data['specs'] = {}

                duplex = self._get_duplex_by_name(inf_data['name'])
                if duplex:
                    inf_data['specs']['duplex'] = duplex

                speed = self._get_speed_by_name(inf_data['name'])
                if speed:
                    inf_data['speed'] = speed

                slot_port = self._get_slot_port_by_name(inf_data['name'])
                if slot_port:
                    inf_data['specs']['slot_port'] = slot_port

            else:
                inf_data['inf_type'] = 'virtual'
                speed = self._get_speed_by_name(inf_data['name'])
                if speed:
                    inf_data['speed'] = speed

            all_interfaces_data.append(inf_data)

        return all_interfaces_data

    @staticmethod
    def _get_duplex_by_name(interface_name: str) -> Optional[str]:
        """Function for getting param duplex for interface by specified name.

        Args:
            interface_name (str): Name of the interface. It's called
                "ifname" in ip-util's output.

        Returns:
            String of duplex param for specified name of the interface.

            None, if there is no duplex for specified interface.

        """
        exec_res = execute(
            'cat',
            f'/sys/class/net/{interface_name}/duplex',
            params=ExecuteParams(  # noqa: S604
                run_as_root=True,
                shell=True,
            ),
        )
        duplex = exec_res.stdout
        return duplex[0].strip() if duplex[0] else None

    @staticmethod
    def _get_speed_by_name(interface_name: str) -> Optional[str]:
        exec_res = execute(
            'cat',
            f'/sys/class/net/{interface_name}/speed',
            params=ExecuteParams(  # noqa: S604
                run_as_root=True,
                shell=True,
            ),
        )
        speed = exec_res.stdout
        return speed[0].strip() if speed[0] else None

    @staticmethod
    def _get_slot_port_by_name(interface_name: str) -> Optional[str]:
        """Function for getting param slot_port for interface by specified name.

        Args:
            interface_name (str): Name of the interface. It's called
                "ifname" in ip-util's output.

        Returns:
            String of slot_port param for specified name of the
                interface.

            None, if there is no slot_port for specified interface.

        """
        exec_res = execute(
            'grep',
            'PCI_SLOT_NAME',
            f'/sys/class/net/{interface_name}/device/uevent',
            params=ExecuteParams(  # noqa: S604
                run_as_root=True,
                shell=True,
            ),
        )
        result = exec_res.stdout
        if result[0]:
            slot_port_match = re.search(r'=(.+)', result[0])
            if slot_port_match:
                return slot_port_match.group(1)

        return None

    @staticmethod
    def _get_physical_interfaces_list() -> List[str]:
        """Function that gets the list of physical interfaces names.

        Returns:
            List of physical interfaces names (List[str]).

        """
        exec_res = execute(
            'ls',
            '-l',
            '/sys/class/net/',
            '|',
            'grep',
            '-v',
            'virtual',
            params=ExecuteParams(  # noqa: S604
                run_as_root=True,
                shell=True,
            ),
        )
        result = exec_res.stdout[0]
        return re.findall(r'/net/(.+)(?:\s|$)', result)

    def get_all(self) -> List:  # noqa: D102
        return self

    def get_interfaces_names(self) -> List:  # noqa: D102
        return [inf['name'] for inf in self]
