"""Management of virtual network interfaces.

This module provides a class for managing virtual network interfaces,
including enabling and disabling the interface.

Classes:
    VirtualInterface: Implementation for managing virtual network
        interfaces.
"""

from openvair.libs.log import get_logger
from openvair.modules.tools.utils import execute
from openvair.modules.network.domain.base import Interface

LOG = get_logger(__name__)


class VirtualInterface(Interface):
    """Implementation for managing virtual network interfaces.

    This class provides methods to enable and disable virtual network
    interfaces.
    """

    def __init__(self, *args, **kwargs):
        """Initialize the VirtualInterface instance.

        This constructor initializes the virtual interface.
        """
        super(VirtualInterface, self).__init__(*args, **kwargs)

    def enable(self) -> None:
        """Enable the virtual network interface.

        This method enables the virtual network interface and logs the process.
        """
        LOG.info(f'Domain layer start enabling virtual interface {self.name}')
        # It may not enable on the first attempt.
        execute('ip', 'link', 'set', self.name, 'up', run_as_root=True)
        LOG.info(
            f'Domain layer successfully enabled virtual interface {self.name}'
        )

    def disable(self) -> None:
        """Disable the virtual network interface.

        This method disables the virtual network interface and logs the process.
        """
        LOG.info(f'Domain layer start disabling virtual interface {self.name}')
        # It may not disable on the first attempt.
        execute('ip', 'link', 'set', self.name, 'down', run_as_root=True)
        LOG.info(
            f'Domain layer successfully disabled virtual interface {self.name}'
        )
