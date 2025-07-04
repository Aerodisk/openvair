"""Module for Libvirt-based virtual machine management.

This module provides a `LibvirtDriver` class for managing virtual machines
using the Libvirt API. It includes methods for starting, stopping, and
managing VNC sessions for virtual machines.

Classes:
    LibvirtDriver: A driver for managing virtual machines using the
        Libvirt API.
"""

from typing import Any, Dict

from openvair.libs.log import get_logger
from openvair.libs.cli.models import ExecuteParams
from openvair.libs.cli.executor import execute
from openvair.libs.cli.exceptions import ExecuteError
from openvair.modules.virtual_machines.config import SERVER_IP
from openvair.modules.virtual_machines.domain.base import BaseLibvirtDriver
from openvair.modules.virtual_machines.domain.exceptions import VNCSessionError

LOG = get_logger(__name__)


class LibvirtDriver(BaseLibvirtDriver):
    """Driver class for managing virtual machines using the Libvirt API.

    This class provides methods to start, stop, and manage VNC sessions
    for virtual machines.

    Attributes:
        vm_info (Dict): Dictionary containing the virtual machine configuration.
        vm_xml (str): The XML definition of the virtual machine.
    """

    def __init__(self, **kwargs: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize a new instance of the LibvirtDriver class.

        Args:
            **kwargs: A dictionary containing the virtual machine
                configuration.
        """
        super(LibvirtDriver, self).__init__()
        self.vm_info = kwargs
        self.vm_xml = self.render_domain(self.vm_info)

    def start(self) -> Dict:
        """Start the virtual machine.

        This method creates a virtual machine using the Libvirt API and
        retrieves its power state, graphic URL, and graphic port.

        Returns:
            Dict: A dictionary containing the power state, URL, and
            port of the virtual machine.

        Raises:
            Exception: If an error occurs while starting the virtual machine.
        """
        LOG.info(f'Starting VM {self.vm_info.get("name")}')
        with self.connection as connection:
            domain = connection.createXML(self.vm_xml)
            state, _ = domain.state()
            domain_xml = domain.XMLDesc()
            graphic_port = self._get_graphic_port_from_xml(domain_xml)
            graphic_url = self._get_graphic_url(domain_xml)

            LOG.info(f'Generated graphic_url: {graphic_url}')
            LOG.info(f'Generated graphic_port: {graphic_port}')

            # Save the graphic interface information
            self.vm_info['graphic_interface'] = {
                'url': f'{graphic_url}:{graphic_port}' if graphic_url else '',
            }

        return {'power_state': state, 'url': graphic_url, 'port': graphic_port}

    def turn_off(self) -> Dict:
        """Turn off the virtual machine.

        This method stops the virtual machine using the Libvirt API.

        Returns:
            Dict: An empty dictionary representing the result of the operation.

        Raises:
            Exception: If an error occurs while turning off the
            virtual machine.
        """
        LOG.info(f'Turning off VM {self.vm_info.get("name")}')
        with self.connection as connection:
            domain = connection.lookupByName(self.vm_info.get('name'))
            domain.destroy()
        return {}

    def vnc(self) -> Dict:
        """Start a VNC session for the virtual machine.

        This method starts a VNC session using the `websockify` tool and
        returns the URL for accessing the VNC session.

        Returns:
            Dict: A dictionary containing the URL of the VNC session.

        Raises:
            ValueError: If the graphic interface URL is not set or is invalid.
            RuntimeError: If starting `websockify` fails.
        """
        LOG.info(f'Starting VNC for VM {self.vm_info.get("name")}')

        graphic_interface = self.vm_info.get('graphic_interface', {})
        LOG.info(f'Graphic interface info: {graphic_interface}')

        vm_url = graphic_interface.get('url')

        if not vm_url:
            LOG.error(
                f'Graphic interface URL not set for VM '
                f'{self.vm_info.get("name")}'
            )
            msg = 'Graphic interface URL is not set'
            raise ValueError(msg)

        try:
            port = vm_url.split(':')[-1]
            vnc_port = f'6{port[1:]}'
        except (AttributeError, IndexError) as err:
            LOG.error(f'Invalid graphic interface URL format: {vm_url}')
            msg = f'Invalid graphic interface URL format: {vm_url}'
            raise ValueError(msg) from err

        try:
            execute(
                'websockify',
                '-D',
                '--run-once',
                '--web',
                '/opt/aero/openvair/openvair/libs/noVNC/',
                vnc_port,
                f'localhost:{port}',
                params=ExecuteParams(  # noqa: S604
                    run_as_root=True, shell=True, raise_on_error=True
                ),
            )
        except (ExecuteError, OSError) as err:
            msg = f'Failed to start websockify: {err!s}'
            LOG.error(msg)
            raise VNCSessionError(msg)

        vnc_url = (
            f'http://{SERVER_IP}:{vnc_port}/vnc.html?'
            f'host={SERVER_IP}&port={vnc_port}'
        )
        return {'url': vnc_url}
