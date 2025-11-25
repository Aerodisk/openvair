"""Factories for template domain models.

This module defines abstract and concrete factory classes for instantiating
template implementations based on disk format (e.g., qcow2).
"""

import abc
from typing import Dict, ClassVar, cast

from openvair.modules.template.domain.base import BaseTemplate

# from openvair.modules.template.adapters.dto.templates import TemplateDomain
from openvair.modules.template.domain.disk_templates.qcow2 import Qcow2Template
from openvair.modules.template.adapters.dto.internal.models import (
    DomainTemplateModelDTO,
)


class AbstractTemplateFactory(metaclass=abc.ABCMeta):
    """Abstract factory for creating template instances."""

    def __call__(self, template_data: Dict) -> BaseTemplate:
        """Creates a template instance from provided data.

        Args:
            template_data (TemplateDomain): Data for creating a template.

        Returns:
            BaseTemplate: The created template instance.
        """
        return self.get_template(template_data)

    @abc.abstractmethod
    def get_template(self, template_data: Dict) -> BaseTemplate:
        """Returns a template instance based on the provided data.

        Args:
            template_data (TemplateDomain): Data for creating a template.

        Returns:
            BaseTemplate: The created template instance.
        """
        ...


class TemplateFactory(AbstractTemplateFactory):
    """Concrete factory for template creation."""

    _template_classes: ClassVar = {
        'qcow2': Qcow2Template,
    }

    def get_template(self, template_data: Dict) -> BaseTemplate:
        """Creates and returns a concrete template instance.

        Selects the appropriate implementation based on `tmp_format`
        (e.g., 'qcow2') and initializes it with validated data.

        Args:
            template_data (Dict): Raw dictionary to build a domain template.

        Returns:
            BaseTemplate: Instantiated domain template.
        """
        dto = DomainTemplateModelDTO.model_validate(template_data)

        template_class = self._template_classes[dto.tmp_format]
        template_manager = template_class(**dto.model_dump())

        return cast(BaseTemplate, template_manager)
