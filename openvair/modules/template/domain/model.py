"""Factories for template domain models.

This module defines abstract and concrete factory classes for creating
template instances.

Classes:
    - AbstractTemplateFactory: Base factory class for template creation.
    - TemplateFactory: Concrete factory for managing templates.
"""

import abc

from openvair.modules.template.domain.base import BaseTemplate
from openvair.modules.template.models.schemas import TemplateData


class AbstractTemplateFactory(metaclass=abc.ABCMeta):
    """Abstract factory for creating template instances."""

    def __call__(self, template_data: TemplateData) -> BaseTemplate:
        """Creates a template instance from provided data.

        Args:
            template_data (TemplateData): Data for creating a template.

        Returns:
            BaseTemplate: The created template instance.
        """
        return self.get_template(template_data)

    @abc.abstractmethod
    def get_template(self, template_data: TemplateData) -> BaseTemplate:
        """Returns a template instance based on the provided data.

        Args:
            template_data (TemplateData): Data for creating a template.

        Returns:
            BaseTemplate: The created template instance.
        """
        ...


class TemplateFactory(AbstractTemplateFactory):
    """Concrete factory for template creation."""

    def get_template(self, template_data: TemplateData) -> BaseTemplate:
        """Creates a template instance.

        This method should be implemented to return a specific template type.

        Args:
            template_data (TemplateData): Data for creating a template.

        Raises:
            NotImplementedError: If not implemented in a subclass.

        Returns:
            BaseTemplate: The created template instance.
        """
        raise NotImplementedError
