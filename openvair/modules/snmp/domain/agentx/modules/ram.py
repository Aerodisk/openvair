"""Module for monitoring RAM usage via SNMP.

This module defines the `Ram` class, which is responsible for monitoring
RAM usage statistics and updating the SNMP agent with the current RAM
usage data.

Classes:
    Ram: Updater class for RAM usage statistics.
"""

import psutil
import pyagentx3 as pyagentx


class Ram(pyagentx.Updater):
    """Updater class for RAM usage statistics.

    This class retrieves RAM usage data and updates the SNMP agent with the
    current RAM usage statistics.
    """

    def update(self) -> None:
        """Update the SNMP agent with the current RAM usage statistics."""
        ram_data = psutil.virtual_memory()

        self.set_COUNTER64('0', ram_data.total)
        self.set_COUNTER64('1', ram_data.used)
        self.set_COUNTER64('2', ram_data.free)
        self.set_COUNTER64('3', ram_data.available)
        self.set_OCTETSTRING('4', ram_data.percent)
