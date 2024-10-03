"""Module for managing unit of work for dashboard operations.

This module defines abstract and concrete unit of work classes for handling
operations related to retrieving Prometheus data for the dashboard.

Classes:
    AbstractUnitOfWork: Abstract base class for unit of work.
    PrometheusUnitOfWork: Concrete implementation for Prometheus.
"""

from __future__ import annotations

import abc

from openvair.modules.dashboard.adapters import repository


class AbstractUnitOfWork(metaclass=abc.ABCMeta):
    """Abstract base class for unit of work.

    This class defines the interface for a unit of work, which manages
    interactions with repositories and ensures proper resource management.
    """

    prometheus: repository.PrometheusRepository

    def __enter__(self) -> AbstractUnitOfWork:
        """Enter the runtime context for the unit of work."""
        return self

    @abc.abstractmethod
    def __exit__(self, *args):
        """Exit the runtime context for the unit of work."""
        pass


class PrometheusUnitOfWork(AbstractUnitOfWork):
    """Concrete unit of work for Prometheus.

    This class provides the implementation for managing Prometheus repository
    interactions, ensuring proper initialization and cleanup of resources.
    """

    def __init__(self):
        """Initialize the PrometheusUnitOfWork.

        This constructor sets up the necessary components for the
        PrometheusUnitOfWork, ensuring proper initialization of the base
        class.
        """
        super().__init__()

    def __enter__(self):
        """Enter the runtime context for the unit of work.

        This method initializes the Prometheus repository and returns the
        instance of the unit of work.
        """
        self.prometheus = repository.PrometheusRepository()
        return super().__enter__()

    def __exit__(self, *args):
        """Exit the runtime context for the unit of work.

        This method ensures proper cleanup of resources when exiting the
        context.
        """
        super().__exit__(*args)
