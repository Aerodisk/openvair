"""Abstract base class for Jinja2 template rendering.

This class implements a 'Template Method' that defines the following steps:
    1) _log_render_start
    2) _prepare_data (abstract, must be overridden)
    3) _render_template
    4) _postprocess_result (abstract, must be overridden)
    5) _log_render_end

Child classes **must** override `_prepare_data` and `_postprocess_result`.
If no processing is required, they should return the input data unchanged.

Attributes:
    env (Environment): Jinja2 environment used for template rendering.
"""

import abc
from typing import Any, Dict
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, TemplateNotFound

from openvair.libs.log import get_logger

LOG = get_logger(__name__)


class BaseTemplateRenderer(abc.ABC):
    """Abstract base class for Jinja2 template rendering.

    Implements the 'Template Method' pattern with the following steps:
        1) _log_render_start
        2) _prepare_data (abstract)
        3) _render_template
        4) _postprocess_result (abstract)
        5) _log_render_end

    Child classes **must** override `_prepare_data` and `_postprocess_result`.
    If no processing is needed, they should return the input unchanged.

    Attributes:
        env (Environment): Jinja2 environment for template rendering.
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
        """
        self._log_render_start(template_name, data)
        prepared_data = self._prepare_data(data)
        rendered_str = self._render_template(template_name, prepared_data)
        final_str = self._postprocess_result(rendered_str)
        self._log_render_end(template_name)
        return final_str

    @abc.abstractmethod
    def _prepare_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data before rendering.

        **This method must be overridden in subclasses** to ensure correct data
        transformation before rendering. If no preprocessing is required, return
        `data` unchanged:

        ```python
        return data
        ```

        🔹 **Why is this method abstract?**
        - Prevents subclasses from accidentally forgetting to implement data
            preparation.
        - Ensures that data is correctly formatted before rendering.
        - Avoids runtime errors where a template expects specific fields but
            receives raw data.

        If `prepare_data` is not needed in a subclass, explicitly override it
            with `return data`.

        Args:
            data (Dict[str, Any]): Raw data.

        Returns:
            Dict[str, Any]: Processed data ready for rendering.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _postprocess_result(self, rendered_str: str) -> str:
        """Post-process the rendered output.

        **This method must be overridden in subclasses** to allow post-rendering
        modifications or cleanup. If no post-processing is needed, return
        `rendered_str` unchanged: ```return rendered_str```

        🔹 **Why is this method abstract?**
        - Ensures that subclasses explicitly define whether post-processing is
            required.
        - Avoids accidental omission, which might lead to incorrect handling of
            rendered data.
        - Supports future modifications where post-processing may become
            necessary.

        If `postprocess_result` is not needed in a subclass, explicitly override
            it with `return rendered_str`.

        Args:
            rendered_str (str): The rendered template.

        Returns:
            str: The final processed output.
        """
        raise NotImplementedError

    def _render_template(self, template_name: str, data: Dict[str, Any]) -> str:
        """Perform the actual Jinja2 rendering.

        Args:
            template_name (str): Name of the template file.
            data (Dict[str, Any]): Prepared data for the template.

        Returns:
            str: The rendered template as a string.

        Raises:
            TemplateNotFound: If the template file is not found.
            Exception: For any error during rendering.
        """
        try:
            LOG.info(f'Rendering template: {template_name} with data: {data}')
            template = self.env.get_template(template_name)
            LOG.info(f"Successfully rendered '{template_name}'")
            return template.render(**data)
        except TemplateNotFound:
            LOG.error(f"Template '{template_name}' not found")
            raise
        except Exception as exc:
            LOG.error(f"Failed to render template '{template_name}': {exc}")
            raise

    def _log_render_start(
        self, template_name: str, data: Dict[str, Any]
    ) -> None:
        """Log the start of the rendering process."""
        LOG.info(f"Start rendering '{template_name}' with data: {data}")

    def _log_render_end(self, template_name: str) -> None:
        """Log the end of the rendering process."""
        LOG.info(f"Finished rendering '{template_name}'")
