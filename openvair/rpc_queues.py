"""Module defining RPC queue names for various services.

This module contains the RPCQueueNames class, which serves as a centralized
repository for RPC queue names used across different services in the system.
Each nested class within RPCQueueNames represents a specific service or module
and contains constants for the corresponding service layer and domain layer
queue names.

The queue names are organized hierarchically, allowing for easy access and
management of RPC communication channels between different parts of the system.

Classes:
    RPCQueueNames: Main class containing nested classes for different modules.
        Each nested class has its own docstring describing its specific purpose.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class RPCQueueNames:
    """Container for RPC queue names used across system modules."""

    @dataclass(frozen=True)
    class Backup:
        """Queue names for backup-related operations."""

        SERVICE_LAYER: str = 'backup_api_service_layer'
        DOMAIN_LAYER: str = 'backup_service_layer_domain'

    @dataclass(frozen=True)
    class BlockDevice:
        """Queue names for block device operations."""

        SERVICE_LAYER: str = 'block_device_api_service_layer'
        DOMAIN_LAYER: str = 'block_device_service_layer_domain'

    @dataclass(frozen=True)
    class Dashboard:
        """Queue names for dashboard operations."""

        SERVICE_LAYER: str = 'dashboard_service_layer'

    @dataclass(frozen=True)
    class Image:
        """Queue names for image-related operations."""

        SERVICE_LAYER: str = 'image_api_service_layer'
        DOMAIN_LAYER: str = 'image_service_layer_domain'

    @dataclass(frozen=True)
    class Network:
        """Queue names for network operations."""

        SERVICE_LAYER: str = 'network_api_service_layer'
        DOMAIN_LAYER: str = 'network_service_layer_domain'

    @dataclass(frozen=True)
    class Notification:
        """Queue names for notification operations."""

        SERVICE_LAYER: str = 'notification_api_service_layer'
        DOMAIN_LAYER: str = 'notification_service_layer_domain'

    @dataclass(frozen=True)
    class SNMP:
        """Queue names for SNMP operations."""

        SERVICE_LAYER: str = 'snmp_service_layer'

    @dataclass(frozen=True)
    class Storage:
        """Queue names for storage operations."""

        SERVICE_LAYER: str = 'storage_api_service_layer'
        DOMAIN_LAYER: str = 'storage_service_layer_domain'

    @dataclass(frozen=True)
    class User:
        """Queue names for user-related operations."""

        SERVICE_LAYER: str = 'api_service_layer_user'

    @dataclass(frozen=True)
    class VMS:
        """Queue names for Virtual Machine module operations."""

        SERVICE_LAYER: str = 'vms_api_service_layer'
        DOMAIN_LAYER: str = 'vms_service_layer_domain'

    @dataclass(frozen=True)
    class VirtualNetwork:
        """Queue names for virtual network operations."""

        SERVICE_LAYER: str = 'virtual_network_api_service_layer'
        DOMAIN_LAYER: str = 'virtual_network_service_layer_domain'

    @dataclass(frozen=True)
    class Volume:
        """Queue names for volume-related operations."""

        SERVICE_LAYER: str = 'volume_api_service_layer'
        DOMAIN_LAYER: str = 'volume_service_layer_domain'

    @dataclass(frozen=True)
    class Template:
        """Queue names for template-related operations."""

        SERVICE_LAYER: str = 'template_api_service_layer'
        DOMAIN_LAYER: str = 'template_service_layer_domain'

    @dataclass(frozen=True)
    class Eventstore:
        """Queue names for eventstore-related operations."""

        SERVICE_LAYER: str = 'eventstore_api_service_layer'
