# noqa: D100
import re
import json
from typing import Dict, List, Optional

from openvair.modules.tools.utils import execute


class GettingSystemInfoError(Exception):  # noqa: D101
    def __init__(self, *args):  # noqa: D107
        super().__init__(args)


class MissingRequiredComponentError(GettingSystemInfoError):  # noqa: D101
    def __init__(self, *args):  # noqa: D107
        super().__init__(args)


class InterfacesFromSystem(list):
    """Custom collection of network interfaces data from system core."""

    def __init__(self):  # noqa: D107
        super().__init__(
            inf_data for inf_data in self._get_all_interfaces_data()
        )

    def _get_all_interfaces_data(self) -> List[Dict]:  # noqa: C901
        """Main function to make the list of interfaces data.

        Returns:
            List[Dict]: List of dictionaries containing data of all
                interfaces.

        """
        all_interfaces_data = []

        sys_output_infs = execute('ip', '-json', 'a')

        if sys_output_infs[1] == '/bin/sh: ip: command not found\n':
            message = (
                "Error in getting interfaces from system, cause util 'ip' not "
                "found."
            )
            raise MissingRequiredComponentError(message)

        if sys_output_infs[1] != '':
            message = (
                f'Error in getting interfaces from system: {sys_output_infs[1]}'
            )
            raise GettingSystemInfoError(message)

        sys_output_infs = json.loads(sys_output_infs[0])

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
        duplex = execute('cat', f'/sys/class/net/{interface_name}/duplex')
        return duplex[0].strip() if duplex[0] else None

    @staticmethod
    def _get_speed_by_name(interface_name: str) -> Optional[str]:
        speed = execute('cat', f'/sys/class/net/{interface_name}/speed')
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
        result = execute(
            'grep',
            'PCI_SLOT_NAME',
            f'/sys/class/net/{interface_name}/device/uevent',
        )
        if result[0]:
            slot_port = re.search(r'=(.+)', result[0]).group(1)
            return slot_port if slot_port else None

        return None

    @staticmethod
    def _get_physical_interfaces_list() -> List[str]:
        """Function that gets the list of physical interfaces names.

        Returns:
            List of physical interfaces names (List[str]).

        """
        result = execute(
            'ls', '-l', '/sys/class/net/', '|', 'grep', '-v', 'virtual'
        )[0]
        return re.findall(r'/net/(.+)(?:\s|$)', result)


    def get_all(self) -> List:  # noqa: D102
        return self

    def get_interfaces_names(self) -> List:  # noqa: D102
        return [inf['name'] for inf in self]
