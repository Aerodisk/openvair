"""Base classes for template domain models.

This module defines abstract base classes for template-related domain models,
providing a foundation for different template types.
"""

import abc
from typing import Dict


class BaseTemplate(metaclass=abc.ABCMeta):
    """Abstract base class for template models."""

    @abc.abstractmethod
    def create(self) -> Dict:  # noqa: D102
        ...

    @abc.abstractmethod
    def edit(self) -> Dict:  # noqa: D102
        ...

    @abc.abstractmethod
    def delete(self) -> Dict:  # noqa: D102
        ...

