"""Factory pattern for creating SNMP agents.

This module defines the `AbstractSNMPFactory` and `SNMPFactory` classes,
which are responsible for creating SNMP agents based on the specified type.

Classes:
    AbstractSNMPFactory: Abstract factory for creating SNMP agents.
    SNMPFactory: Concrete factory for creating SNMP agents.
"""

import abc
from typing import ClassVar

from openvair.modules.snmp.domain.base import BaseSNMP
from openvair.modules.snmp.domain.agentx import agentx
from openvair.modules.snmp.domain.exceptions import SNMPAgenTypeError


class AbstractSNMPFactory(metaclass=abc.ABCMeta):
    """Abstract factory for creating SNMP agents.

    This abstract factory defines the interface for creating
    SNMP agents of various types.
    """

    @abc.abstractmethod
    def get_snmp_agent(self, snmp_type: str) -> BaseSNMP:
        """Create an SNMP agent of the specified type.

        Args:
            snmp_type (str): The type of SNMP agent to create.

        Returns:
            BaseSNMP: An instance of an SNMP agent.
        """
        ...


class SNMPFactory(AbstractSNMPFactory):
    """Concrete factory for creating SNMP agents.

    This factory creates SNMP agents of different types based on the provided
    type identifier.
    """

    _snmp_classes: ClassVar = {
        'agentx': agentx.SNMPAgentx,
    }

    def get_snmp_agent(self, snmp_type: str) -> BaseSNMP:
        """Create an SNMP agent of the specified type.

        Args:
            snmp_type (str): The type of SNMP agent to create.

        Returns:
            BaseSNMP: An SNMP agent object of the specified type.

        Raises:
            SNMPAgenTypeError: If the specified SNMP agent type is not found.
        """
        snmp_class = self._snmp_classes.get(snmp_type)

        if not snmp_class:
            message = f"SNMP type '{snmp_type}' not found"
            raise SNMPAgenTypeError(message)

        return snmp_class()
