"""Module for monitoring CPU usage via SNMP.

This module defines the `Cpu` class, which is responsible for monitoring
CPU usage statistics and updating the SNMP agent with the current CPU
usage data.

Classes:
    Cpu: Updater class for CPU usage statistics.
"""

import psutil
import pyagentx3 as pyagentx


class Cpu(pyagentx.Updater):
    """Updater class for CPU usage statistics.

    This class retrieves CPU usage data and updates the SNMP agent with the
    current CPU usage and the number of CPU cores.
    """

    def _get_cpu_usage(self) -> str:
        """Retrieve the current CPU usage percentage.

        Returns:
            str: The current CPU usage percentage as a string.
        """
        cpu_usage_percent = round(psutil.cpu_percent(), 2)
        return str(cpu_usage_percent)

    def update(self) -> None:
        """Update the SNMP agent with the current CPU usage statistics."""
        self.set_INTEGER('0', psutil.cpu_count())
        self.set_OCTETSTRING('1', self._get_cpu_usage())
