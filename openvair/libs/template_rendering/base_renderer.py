"""Abstract base class for Jinja2 template rendering.

This class implements a 'Template Method' that defines the following
steps:
    1) _log_render_start
    2) prepare_data
    3) _render_template
    4) postprocess_result
    5) _log_render_end

Child classes should provide their own template directory path and
may override prepare_data or postprocess_result.

Attributes:
    env (Environment): Jinja2 environment used for template rendering.
"""

from typing import Any, Dict
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, TemplateNotFound

from openvair.libs.log import get_logger

LOG = get_logger(__name__)


class BaseTemplateRenderer:
    """Abstract base class for Jinja2 template rendering.

    This class implements a 'Template Method' that defines the following steps:
        1) _log_render_start
        2) prepare_data
        3) _render_template
        4) postprocess_result
        5) _log_render_end

    Child classes should define `TEMPLATE_SUBDIR` to specify where templates
    are located relative to the module.

    Attributes:
        env (Environment): Jinja2 environment used for template rendering.
    """

    TEMPLATE_SUBDIR: str = 'templates'

    def __init__(self, module_path: str) -> None:
        """Initialize the renderer with the computed template directory.

        Args:
            module_path (str): The `__file__` path of the module using this
                renderer.
        """
        template_dir = Path(module_path).parent / self.TEMPLATE_SUBDIR
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=True,
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def render(self, template_name: str, data: Dict[str, Any]) -> str:
        """Render the given template with the provided data.

        Args:
            template_name (str): Name of the Jinja2 template file.
            data (Dict[str, Any]): Data for rendering the template.

        Returns:
            str: The rendered result.

        Raises:
            FileNotFoundError: If the template file is not found.
            TemplateNotFound: If the template cannot be found.
            Exception: For any error during rendering.
        """
        self._log_render_start(template_name, data)
        prepared_data = self.prepare_data(data)
        rendered_str = self._render_template(template_name, prepared_data)
        final_str = self.postprocess_result(rendered_str)
        self._log_render_end(template_name)
        return final_str

    def prepare_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data before rendering (hook method).

        Child classes may override this method to validate or transform
        the data.

        Args:
            data (Dict[str, Any]): Raw data dictionary.

        Returns:
            Dict[str, Any]: Processed data dictionary.
        """
        return data

    def postprocess_result(self, rendered_str: str) -> str:
        """Post-process the rendered output (hook method).

        Child classes may override this method to transform the output.

        Args:
            rendered_str (str): The rendered string output.

        Returns:
            str: The final output string.
        """
        return rendered_str

    def _render_template(self, template_name: str, data: Dict[str, Any]) -> str:
        """Perform the actual Jinja2 rendering.

        Args:
            template_name (str): Name of the template file.
            data (Dict[str, Any]): Prepared data for the template.

        Returns:
            str: The rendered template as a string.

        Raises:
            TemplateNotFound: If the template file is not found.
            FileNotFoundError: If the template file is missing.
            Exception: For any error during rendering.
        """
        try:
            template = self.env.get_template(template_name)
            rendered_str = template.render(**data)
        except TemplateNotFound:
            LOG.error(f"Template '{template_name}' not found")
            raise
        except Exception as exc:
            LOG.error(f"Failed to render template '{template_name}': {exc}")
            raise
        else:
            return rendered_str

    def _log_render_start(
        self, template_name: str, data: Dict[str, Any]
    ) -> None:
        """Log the start of the rendering process.

        Args:
            template_name (str): Name of the template file.
            data (Dict[str, Any]): Data used for rendering.
        """
        LOG.info(f"Start rendering '{template_name}' with data: {data}")

    def _log_render_end(self, template_name: str) -> None:
        """Log the end of the rendering process.

        Args:
            template_name (str): Name of the template file.
        """
        LOG.info(f"Finished rendering '{template_name}'")
