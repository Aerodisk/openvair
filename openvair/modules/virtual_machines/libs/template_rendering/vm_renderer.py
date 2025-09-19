"""Virtual Machine rendering module.

This module provides a `VMRenderer` class responsible for rendering
XML templates for virtual machine configurations.

Classes:
    VMRenderer: A renderer specialized for VM XML configurations.
"""

from typing import Any

from openvair.libs.log import get_logger
from openvair.libs.template_rendering.base_renderer import BaseTemplateRenderer

LOG = get_logger(__name__)


class VMRenderer(BaseTemplateRenderer):
    """Renderer for virtual machine XML configurations.

    Inherits from BaseTemplateRenderer to leverage the Template Method pattern.

    Attributes:
        DOMAIN_XML_TEMPLATE (str): Filename for the VM domain XML template.
    """

    DOMAIN_XML_TEMPLATE: str = 'domain.xml'

    def __init__(self) -> None:
        """Initialize with the virtual machine package templates."""
        super().__init__(module_path=__file__)

    def render_domain(self, raw_data: dict[str, Any]) -> str:
        """Create an XML configuration for a virtual machine domain.

        Args:
            raw_data (Dict[str, Any]): Virtual machine configuration parameters.

        Returns:
            str: The rendered XML configuration.
        """
        LOG.info(f"Start rendering domain XML for VM: {raw_data.get('name')}")
        xml_result = self.render(self.DOMAIN_XML_TEMPLATE, raw_data)
        LOG.info(
            f"Finished rendering domain XML for VM: {raw_data.get('name')}"
        )
        return xml_result

    def _prepare_data(self, data: dict[str, Any]) -> dict[str, Any]:
        return data

    def _postprocess_result(self, rendered_str: str) -> str:
        return rendered_str
