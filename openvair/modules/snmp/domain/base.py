"""Base class for SNMP configuration.

This module defines the `BaseSNMP` class, which serves as an abstract base
class for configuring SNMP agents.

Classes:
    BaseSNMP: Abstract base class for SNMP configuration.
"""

import abc


class BaseSNMP(metaclass=abc.ABCMeta):
    """Abstract base class for SNMP configuration.

    This class defines the interface for configuring SNMP agents.
    Subclasses should implement the `setup` method to specify how
    SNMP should be set up.
    """

    @abc.abstractmethod
    def setup(self) -> None:
        """Set up the SNMP configuration.

        This method should be implemented to configure the SNMP agent
        according to the specific requirements of the subclass.
        """
        ...
