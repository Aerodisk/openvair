"""Module for monitoring network interface status via SNMP.

This module defines the `Networks` class, which is responsible for monitoring
network interface status and updating the SNMP agent with the current network
interface data.

Classes:
    Networks: Updater class for network interface status.
"""

from typing import cast

import psutil
import pyagentx3 as pyagentx
from psutil._common import snicstats


class Networks(pyagentx.Updater):
    """Updater class for network interface status.

    This class retrieves network interface statistics and updates the SNMP
    agent with the current network interface status.
    """

    def _get_networks(self) -> dict[str, snicstats]:
        """Retrieve network interface statistics.

        Returns:
           Dict: A dictionary of network interfaces and their status.
        """
        return cast('dict', psutil.net_if_stats())

    def update(self) -> None:
        """Update the SNMP agent with the current network interface status."""
        network_dict = self._get_networks()
        for index, interface_name in enumerate(network_dict):
            counter = 0
            self.set_OCTETSTRING(f'{index}.{counter}', interface_name)
            interface_snicstats: snicstats = network_dict[interface_name]
            self.set_OCTETSTRING(
                f'{index}.{counter+1}',
                str(interface_snicstats.isup),
            )
