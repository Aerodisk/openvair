"""Network rendering module.

This module provides classes and functions to generate YAML configurations
for network components. It uses the Template Method approach with Jinja2 and
PackageLoader to render templates.

Classes:
    NetworkRenderer: A renderer specialized for network YAML configurations.
"""

from typing import Any, Dict

from openvair.libs.log import get_logger
from openvair.libs.template_rendering.base_renderer import BaseTemplateRenderer

LOG = get_logger(__name__)


class NetworkRenderer(BaseTemplateRenderer):
    """Renderer for network YAML configurations.

    Inherits from BaseTemplateRenderer to leverage the Template Method
    pattern.

    Attributes:
        OVS_YAML_TEMPLATE (str): Filename for the OVS bridge netplan YAML
            template.
        PORT_YAML_TEMPLATE (str): Filename for the interface (port) netplan YAML
            template.
    """

    OVS_YAML_TEMPLATE: str = 'netplan_bridge_template.yaml.j2'
    PORT_YAML_TEMPLATE: str = 'port_netplan_template.yaml.j2'

    def __init__(self) -> None:
        """Initialize with the network package templates."""
        super().__init__(
            package_name='openvair.modules.network.libs.templating',
            package_path='templates',
        )

    def create_ovs_bridge_netplan_yaml(self, raw_data: Dict[str, Any]) -> str:
        """Create a YAML configuration for an OVS bridge (Netplan).

        This method calls `self.render` following these steps:
            1) _log_render_start
            2) prepare_data
            3) _render_template
            4) postprocess_result
            5) _log_render_end

        Args:
            raw_data (Dict[str, Any]): OVS bridge parameters.

        Returns:
            str: The rendered YAML configuration.
        """
        LOG.info(
            f"Start rendering OVS bridge netplan for: "
            f"{raw_data.get('bridge_name')}"
        )
        yaml_result = self.render(self.OVS_YAML_TEMPLATE, raw_data)
        LOG.info(
            f"Finished rendering OVS bridge netplan for: "
            f"{raw_data.get('bridge_name')}"
        )
        return yaml_result

    def create_iface_yaml(self, raw_data: Dict[str, Any]) -> str:
        """Create a YAML configuration for a network interface.

        This method calls `self.render` following these steps:
            1) _log_render_start
            2) prepare_data
            3) _render_template
            4) postprocess_result
            5) _log_render_end

        Args:
            raw_data (Dict[str, Any]): Interface parameters.

        Returns:
            str: The rendered YAML configuration.
        """
        LOG.info(
            f"Start rendering interface YAML for: " f"{raw_data.get('name')}"
        )
        yaml_result = self.render(self.PORT_YAML_TEMPLATE, raw_data)
        LOG.info(
            f"Finished rendering interface YAML for: " f"{raw_data.get('name')}"
        )
        return yaml_result
