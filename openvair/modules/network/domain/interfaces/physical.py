"""Management of physical network interfaces.

This module provides a class for managing physical network interfaces,
including enabling and disabling the interface.

Classes:
    PhysicalInterface: Implementation for managing physical network
        interfaces.
"""

from typing import Any

from openvair.libs.log import get_logger
from openvair.modules.tools.utils import execute
from openvair.modules.network.domain.base import BaseInterface

LOG = get_logger(__name__)


class PhysicalInterface(BaseInterface):
    """Implementation for managing physical network interfaces.

    This class provides methods to enable and disable physical network
    interfaces.

    Attributes:
        duplex (str): The duplex setting for the interface.
        slot_port (str): The slot port identifier for the interface.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize the PhysicalInterface instance.

        This constructor initializes the physical interface with optional
        duplex and slot port settings.
        """
        super(PhysicalInterface, self).__init__(*args, **kwargs)
        self.duplex = kwargs.pop('duplex', '')
        self.slot_port = kwargs.pop('slot_port', '')

    def enable(self) -> None:
        """Enable the physical network interface.

        This method enables the physical network interface and logs the process.
        """
        LOG.info(f'Domain layer start enabling physical interface {self.name}')
        # It may not enable on the first attempt.
        execute('ip', 'link', 'set', self.name, 'up', run_as_root=True)
        LOG.info(
            f'Domain layer successfully enabled physical interface {self.name}'
        )

    def disable(self) -> None:
        """Disable the physical network interface.

        This method disables the physical network interface and logs the
        process.
        """
        LOG.info(f'Domain layer start disabling physical interface {self.name}')
        # It may not disable on the first attempt.
        execute('ip', 'link', 'set', self.name, 'down', run_as_root=True)
        LOG.info(
            f'Domain layer successfully disabled physical interface {self.name}'
        )
