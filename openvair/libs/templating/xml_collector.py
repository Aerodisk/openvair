"""XML configuration generator for app modules.

This module provides a function to generate an XML configuration for an app
modules using Jinja2 templates. The generated XML is based on the provided data.

Functions:
    create_virtual_network_xml: Creates an XML configuration for a virtual
        network based on the provided data.
"""

from typing import Dict
from pathlib import Path

from jinja2 import Template

from openvair.libs.log import get_logger
from openvair.libs.templating.config import TEMPLATES_DIR

LOG = get_logger(__name__)


def create_virtual_network_xml(vn_data: Dict) -> str:
    """Creates XML configuration for a virt. network based on the provided data.

    This function uses a Jinja2 template to render an XML configuration for a
    virtual network. The template is populated with the data provided in the
    `vn_data` dictionary.

    Args:
        vn_data (Dict): A dictionary containing information about the virtual
            network.
            Required keys:
                - 'id': The UUID of the virtual network.
                - 'network_name': The name of the virtual network.
                - 'forward_mode': The forward mode of the virtual network.
                - 'bridge': The bridge name of the virtual network.
                - 'virtual_port_type': The type of virtual port.
                - 'port_groups': List of port groups for the virtual network.

    Returns:
        str: The XML configuration for the virtual network.

    Raises:
        FileNotFoundError: If the network template file is not found.
        Exception: Any other error that occurs during rendering.
    """
    virtual_network_template = 'bridge_virtual_network_template.xml.j2'
    template_path = f'{TEMPLATES_DIR}/{virtual_network_template}'

    try:
        with Path(template_path).open('r') as tmp_file:
            LOG.info(
                f"Start rendering network XML for network: "
                f"{vn_data.get('network_name')}"
            )

            template_content = tmp_file.read()
            template = Template(
                template_content,
                trim_blocks=True,
                lstrip_blocks=True,
                autoescape=True,
            )
            xml_virtual_network = template.render(
                uuid=vn_data.get('id'),
                network_name=vn_data.get('network_name'),
                forward_mode=vn_data.get('forward_mode'),
                bridge_name=vn_data.get('bridge'),
                virtual_port_type=vn_data.get('virtual_port_type'),
                port_groups=vn_data.get('port_groups'),
            )

        LOG.info(
            "Finished rendering network XML for network: "
            f"{vn_data.get('network_name')}"
        )

    except FileNotFoundError:
        LOG.error(f'Template file not found: {template_path}')
        raise

    except Exception as e:
        LOG.error(f'Error rendering network XML: {e!s}')
        raise

    else:
        return xml_virtual_network
