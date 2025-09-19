"""Module for monitoring disk usage via SNMP.

This module defines the `Disks` class, which is responsible for monitoring
disk usage statistics and updating the SNMP agent with the current disk
usage data.

Classes:
    Disks: Updater class for disk usage statistics.
"""


import psutil
import pyagentx3 as pyagentx
from psutil._common import sdiskpart


class Disks(pyagentx.Updater):
    """Updater class for disk usage statistics.

    This class retrieves disk usage data and updates the SNMP agent with
    the current disk usage statistics for each disk partition.
    """

    def get_disks_data(self) -> list[sdiskpart]:
        """Retrieve disk partition information.

        Returns:
            List[psutil._common.sdiskpart]: A list of disk partitions.
        """
        result: list[sdiskpart] = psutil.disk_partitions()
        return result

    def update(self) -> None:
        """Update the SNMP agent with the current disk usage statistics."""
        for index, disk in enumerate(self.get_disks_data()):
            counter = 0
            disk_size_data = psutil.disk_usage(disk.mountpoint)

            self.set_OCTETSTRING(f'{index}.{counter}', disk.device)
            self.set_OCTETSTRING(f'{index}.{counter+1}', disk.fstype)
            self.set_OCTETSTRING(f'{index}.{counter+2}', disk.mountpoint)

            self.set_COUNTER64(
                f'{index}.{counter+3}.{counter}', disk_size_data.total
            )
            self.set_COUNTER64(
                f'{index}.{counter+3}.{counter+1}', disk_size_data.used
            )
