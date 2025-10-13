"""Virtual Network rendering module.

This module provides classes and functions to generate XML
configurations related to virtual networks. It uses the Template Method
approach to keep a consistent rendering workflow.

Classes:
    VirtualNetworkRenderer: A renderer specialized for virtual network
        XML configurations.
"""

from typing import Any

from openvair.libs.log import get_logger
from openvair.libs.template_rendering.base_renderer import BaseTemplateRenderer

LOG = get_logger(__name__)


class VirtualNetworkRenderer(BaseTemplateRenderer):
    """Renderer for virtual network XML configurations.

    Inherits from BaseTemplateRenderer to leverage the Template Method
    pattern.

    Attributes:
        XML_TEMPLATE (str): Filename for the XML template.
    """

    XML_TEMPLATE: str = 'bridge_virtual_network_template.xml.j2'

    def __init__(self) -> None:
        """Initialize with the virtual network package templates."""
        super().__init__(module_path=__file__)

    def create_virtual_network_xml(self, raw_data: dict[str, Any]) -> str:
        """Create an XML configuration for a virtual network.

        This method calls `self.render` following these steps:
            1) _log_render_start
            2) prepare_data
            3) _render_template
            4) postprocess_result
            5) _log_render_end

        Args:
            raw_data (Dict[str, Any]): Virtual network parameters.

        Returns:
            str: The rendered XML configuration.
        """
        LOG.info(
            f"Start rendering network XML for network: "
            f"{raw_data.get('network_name')}"
        )
        xml_result = self.render(self.XML_TEMPLATE, raw_data)
        LOG.info(
            f"Finished rendering network XML for network: "
            f"{raw_data.get('network_name')}"
        )
        return xml_result

    def _prepare_data(self, data: dict[str, Any]) -> dict[str, Any]:
        return {
            'uuid': data.get('id'),
            'network_name': data.get('network_name'),
            'forward_mode': data.get('forward_mode'),
            'bridge_name': data.get('bridge'),
            'virtual_port_type': data.get('virtual_port_type'),
            'port_groups': data.get('port_groups', []),
        }

    def _postprocess_result(self, rendered_str: str) -> str:
        return rendered_str  # No post-processing needed
