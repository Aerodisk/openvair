"""Module for managing Fibre Channel (FC) device connections.

This module provides the `FibreChannelInterface` class, which is responsible for
managing Fibre Channel device connections, including the ability to perform a
LIP (Loop Initialization Procedure) scan.

The class inherits from the `BaseFibreChannel` abstract base class, which
defines the common interface for Fibre Channel block device interfaces.

The module also includes a custom exception, `LipScanError`, which is used to
handle any errors that may occur during the LIP scan process.

Classes:
    FibreChannelInterface: Provides functionality to manage Fibre Channel
        devices.
"""

from openvair.libs.log import get_logger
from openvair.modules.block_device.libs.utils import lip_scan as utils_lip_scan
from openvair.modules.block_device.domain.base import BaseFibreChannel
from openvair.modules.block_device.domain.exceptions import (
    LipScanError,
)

LOG = get_logger(__name__)


class FibreChannelInterface(BaseFibreChannel):
    """Class providing functionality to manage FC devices.

    This class inherits from the `BaseFibreChannel` abstract class and provides
    a concrete implementation for performing a LIP scan on Fibre Channel host
    adapters.
    """

    def __init__(self) -> None:
        """Initialize a FibreChannelInterface object.

        Args:
            *args: Positional arguments passed to the `BaseFibreChannel`
                constructor.
            **kwargs: Keyword arguments passed to the `BaseFibreChannel`
                constructor.
        """
        super().__init__()

    def lip_scan(self) -> str:
        """Perform a LIP (Loop Initialization Procedure) scan.

        Returns:
            str: The result of the LIP scan.

        Raises:
            LipScanError: If an error occurs during the LIP scan process.
        """
        try:
            LOG.info('Starting to scan on Fibre Channel host adapters...')
            utils_lip_scan()
            message = (
                'Successful finished to scan on Fibre Channel ' 'host adapters.'
            )
            LOG.info(message)
        except OSError as error:
            message = f'Failed to scan on Fibre Channel host adapters: {error}'
            LOG.error(message)
            raise LipScanError(message)
        else:
            return message
