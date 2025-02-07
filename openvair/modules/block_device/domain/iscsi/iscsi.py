"""Module for managing ISCSI connections.

This module provides the `ISCSIInterface` class, which is responsible for
managing ISCSI connections, including discovery, login, and logout operations.
The class inherits from the `BaseISCSI` abstract base class, which defines the
common interface for block device interfaces.

The module also includes several custom exceptions, such as `ISCSILoginError`,
`ISCSILogoutError`, `ISCSIDiscoveryError`, `ISCSIGetIQNException`, and
`ISCSIIqnNotFoundException`, which are used to handle various errors that may
occur during the ISCSI connection management process.

Classes:
    ISCSIInterface: Provides functionality to manage ISCSI connections.
"""

from typing import Any, Dict

from openvair.libs.log import get_logger
from openvair.libs.cli.models import ExecuteParams
from openvair.libs.cli.executor import execute
from openvair.libs.cli.exceptions import ExecuteError
from openvair.modules.block_device.domain.base import BaseISCSI
from openvair.modules.block_device.domain.exceptions import (
    ISCSILoginError,
    ISCSILogoutError,
    ISCSIDiscoveryError,
    ISCSIGetIQNException,
    ISCSIIqnNotFoundException,
)

LOG = get_logger(__name__)


class ISCSIInterface(BaseISCSI):
    """Class providing functionality to manage iSCSI connections.

    This class inherits from the `BaseISCSI` abstract class and provides
    concrete implementations for managing iSCSI connections, including
    discovery, login, and logout operations.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize an ISCSIInterface object.

        Args:
            *args: Positional arguments passed to the `BaseISCSI` constructor.
            **kwargs: Keyword arguments passed to the `BaseISCSI` constructor.
        """
        super().__init__(*args, **kwargs)

    def get_host_iqn(self) -> str:
        """Get the IQN of the host initiator.

        Returns:
            str: The IQN of the host initiator.

        Raises:
            ISCSIGetIQNException: If an error occurs while retrieving the IQN.
        """
        LOG.info('Start getting the IQN of the host initiator.')
        command = 'cat /etc/iscsi/initiatorname.iscsi'
        try:
            exec_res = execute(
                command,
                params=ExecuteParams(  # noqa: S604
                    run_as_root=True,
                    shell=True,
                    raise_on_error=True,
                ),
            )
        except ExecuteError as err:
            message = f'Error while getting host iqn: {err}'
            LOG.error(message)
            raise ISCSIGetIQNException(message)

        iqn = self._get_iqn_from_string(exec_res.stdout)
        LOG.info(f'Got the IQN of the host initiator: {iqn}')
        return iqn

    def discovery(self) -> str:
        """Discover iSCSI target on the specified IP address.

        Returns:
            str: The discovered iSCSI IQN.

        Raises:
            ISCSIDiscoveryError: If an error occurs during the discovery
                process.
        """
        LOG.info(f'Start to discover iSCSI target IQN on the IP: {self.ip}')
        command = f'iscsiadm -m discovery -t st -p {self.ip}:{self.port}'
        try:
            exec_res = execute(
                command,
                params=ExecuteParams(  # noqa: S604
                    run_as_root=True,
                    shell=True,
                    raise_on_error=True,
                ),
            )
        except ExecuteError as err:
            message = f'Error while discovering ISCSI target IQN: {err}'
            LOG.error(message)
            raise ISCSIDiscoveryError(message)

        discovered_iqn = self._get_discovered_iqn(exec_res.stdout)
        LOG.info(f'Discovered ISCSI target IQN: {discovered_iqn}')
        return discovered_iqn

    def login(self) -> Dict:
        """Log in to the specified iSCSI target.

        Returns:
            Dict: The ISCSIInterface object as a dictionary.

        Raises:
            ISCSILoginError: If an error occurs during the login process.
        """
        LOG.info(f'Start to login to the iSCSI target: {self.ip}')
        discovered_iqn = self.discovery()
        command = (
            f'iscsiadm -m node -T {discovered_iqn} -p'
            f' {self.ip}:{self.port} --login'
        )
        try:
            execute(
                command,
                params=ExecuteParams(  # noqa: S604
                    run_as_root=True,
                    shell=True,
                    raise_on_error=True,
                ),
            )
        except ExecuteError as err:
            message = f'Failed to login: {err}'
            LOG.error(message)
            raise ISCSILoginError(message)

        LOG.info('Successfully logged in')
        return self.__dict__

    def logout(self) -> Dict:
        """Log out from the specified iSCSI target.

        Returns:
            Dict: The ISCSIInterface object as a dictionary.

        Raises:
            ISCSILogoutError: If an error occurs during the logout process.
        """
        LOG.info(f'Start to logging out from the ISCSI target: {self.ip}')
        discovered_iqn = self.discovery()
        command = (
            f'iscsiadm -m node -T {discovered_iqn} -p'
            f' {self.ip}:{self.port} --logout'
        )
        try:
            execute(
                command,
                params=ExecuteParams(  # noqa: S604
                    run_as_root=True,
                    shell=True,
                    raise_on_error=True,
                ),
            )
        except ExecuteError as err:
            message = f'Failed to logout: {err}'
            LOG.error(message)
            raise ISCSILogoutError(message)

        LOG.info('Successfully logged out')
        return self.__dict__

    @staticmethod
    def _get_discovered_iqn(string: str) -> str:
        """Extract the iSCSI IQN from the provided string.

        Args:
            string (str): The string containing the iSCSI IQN.

        Returns:
            str: The extracted iSCSI IQN.
        """
        LOG.info(f'Start getting targets iSCSI IQN from a raw string: {string}')
        iqn_value = string.split()[-1]
        LOG.info(f'Extracted iSCSI IQN: {iqn_value}')
        return iqn_value

    @staticmethod
    def _get_iqn_from_string(string: str) -> str:
        """Extract the IQN from the provided string.

        Args:
            string (str): The string containing the IQN.

        Returns:
            str: The extracted IQN.

        Raises:
            ISCSIIqnNotFoundException: If the IQN cannot be found in the string.
        """
        LOG.info(f'Start getting IQN from a raw string: {string}')
        # Find the starting position of the string 'InitiatorName='
        start_index = string.find('InitiatorName=')

        # If the string is found
        if start_index != -1:
            # Get the substring starting from the position after
            # 'InitiatorName='
            return string[start_index + len('InitiatorName=') :].strip()

        message = f'Failed to find IQN number from string: {string}'
        LOG.error(message)
        raise ISCSIIqnNotFoundException(message)
