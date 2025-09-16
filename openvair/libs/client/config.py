"""Module for handling configuration-related utilities.

This module provides various utility functions for retrieving configuration
data such as URLs, credentials, and settings from the project configuration.
It also handles the initialization of external services like Sentry.

Functions:
    get_web_app_url: Retrieves the web application URL from the config.
    get_prometheus_url: Retrieves the Prometheus service URL from the config.
    get_default_user: Retrieves the default user credentials.
    get_snmp_agent: Retrieves the SNMP agent type.
    get_os_type: Retrieves the operating system type.
    get_routes: Retrieves the routes for the documentation, if available.
    get_sentry_dsn: Initializes Sentry if a DSN is provided in the config.
    _check_docs_routes: Checks if the documentation routes exist.
    _set_sentry_dsn: Sets the Sentry DSN for error tracking.
"""

import pathlib
from typing import Any, Dict, Tuple

import sentry_sdk

from openvair import config


def get_web_app_url() -> str:
    """Retrieve the web application URL from the config.

    This function reads the `web_app` configuration and constructs the URL
    for the web application based on the host and port specified.

    Returns:
        str: The URL of the web application.
    """
    web_app = config.data.get('web_app', {})
    host = web_app.get('host', 'localhost')
    port = web_app.get('port', 8000)
    return f'https://{host}:{port}'


def get_prometheus_url() -> str:
    """Retrieve the Prometheus service URL from the config.

    This function reads the `prometheus` configuration and constructs the URL
    for the Prometheus service based on the host and port specified.

    Returns:
        str: The URL of the Prometheus service.
    """
    prometheus_app = config.data.get('prometheus', {})
    host = prometheus_app.get('host', 'localhost')
    port = prometheus_app.get('port', 9090)
    return f'https://{host}:{port}'


def get_default_user() -> Tuple[str, str]:
    """Retrieve the default user credentials from the config.

    This function reads the `default_user` configuration and returns the
    login and password for the default user.

    Returns:
        Tuple[str, str]: A tuple containing the login and password.
    """
    default_user = config.data.get('default_user', {})
    login = default_user.get('login', '')
    password = default_user.get('password', '')
    return login, password


def get_snmp_agent() -> str:
    """Retrieve the SNMP agent type from the config.

    This function reads the `snmp` configuration and returns the specified
    SNMP agent type.

    Returns:
        str: The type of SNMP agent.
    """
    snmp: Dict[str, str] = config.data.get('snmp', {})
    return snmp.get('agent_type', '')


def get_os_type() -> str:
    """Retrieve the operating system type from the config.

    This function reads the `OS_data` configuration and returns the specified
    operating system type.

    Returns:
        str: The name of the operating system.
    """
    os_data: Dict[str, str] = config.data.get('OS_data', {})
    return os_data.get('os_type', 'ubuntu')


def _check_docs_routes() -> bool:
    """Check if the documentation routes exist.

    This function checks the existence of specific directories related to the
    documentation routes.

    Returns:
        bool: True if the documentation routes exist, False otherwise.
    """
    docs_folder_path = f'{config.PROJECT_ROOT}/docs'
    build_folder_path = f'{docs_folder_path}/build'
    entrypoints_folder_path = f'{build_folder_path}/entrypoints'

    return any(
        [
            pathlib.Path(docs_folder_path).exists(),
            pathlib.Path(build_folder_path).exists(),
            pathlib.Path(entrypoints_folder_path).exists(),
        ]
    )


def get_routes() -> Any:  # noqa: ANN401
    """Retrieve the routes for the documentation, if available.

    This function checks if the documentation routes exist and returns them.
    If they do not exist or if there is an error, it returns None.

    Returns:
        Optional: Documentation routes if available, otherwise None.
    """
    routes = None

    try:
        if _check_docs_routes():
            from docs.entrypoints.api import docs_routes  # noqa: PLC0415

            routes = docs_routes()
    except ImportError:
        pass

    return routes


def get_sentry_dsn() -> None:
    """Initialize Sentry if a DSN is provided in the config.

    This function retrieves the Sentry DSN from the configuration and
    initializes Sentry for error tracking if the DSN is specified.
    """
    sentry_dsn = config.data.get('sentry', {}).get('dsn')
    if sentry_dsn:
        _set_sentry_dsn(sentry_dsn)


def _set_sentry_dsn(sentry_dsn: str) -> None:
    """Set the Sentry DSN for error tracking.

    This function configures Sentry with the provided DSN token.

    Args:
        sentry_dsn (str): The Sentry DSN token.
    """
    sentry_sdk.init(
        dsn=sentry_dsn,
        traces_sample_rate=1.0,
    )


PROMETHEUS_QUERIES = {
    # Prometheus queries for various metrics.
    'io-read-ps': {
        'query': 'sum(rate(node_disk_reads_completed_total[30s]))',
        'unit': 'io-ps',
    },
    'io-write-ps': {
        'query': 'sum(rate(node_disk_writes_completed_total[30s]))',
        'unit': 'io-ps',
    },
    'bandwidth-read': {
        'query': (
            'sum(rate(node_network_receive_bytes_total[30s])) / 1024 / 1024'
        ),
        'unit': 'b/s',
    },
    'bandwidth-write': {
        'query': (
            'sum(rate(node_network_transmit_bytes_total[30s])) / 1024 / 1024'
        ),
        'unit': 'b/s',
    },
    'disk-read': {
        'query': 'sum(rate(node_disk_read_bytes_total[30s])) / 1024 / 1024',
        'unit': 'b/s',
    },
    'disk-write': {
        'query': 'sum(rate(node_disk_written_bytes_total[30s])) / 1024 / 1024',
        'unit': 'b/s',
    },
    'latency': {
        'query': 'irate(node_pressure_io_waiting_seconds_total[30s])',
        'unit': 's',
    },
    'ram-total': {
        'query': 'node_memory_MemTotal_bytes',
        'unit': 'B',
    },
    'ram-free': {
        'query': 'node_memory_MemFree_bytes',
        'unit': 'B',
    },
    'ram-used': {
        # This query calculates the total amount of memory used by the node or
        # computer in bytes by subtracting free memory, buffered memory,
        # cached memory, and reclaimable memory from total memory.
        'query': 'node_memory_MemTotal_bytes - node_memory_MemFree_bytes'
        '- node_memory_Buffers_bytes - node_memory_Cached_bytes'
        '- node_memory_SReclaimable_bytes',
        'unit': 'B',
    },
    'ram-available': {'query': 'node_memory_MemAvailable_bytes', 'unit': 'B'},
    'ram-commited': {'query': 'node_memory_Committed_AS_bytes', 'unit': 'B'},
    'cpu-seconds-total': {
        'query': 'sum(node_cpu_scaling_frequency_hertz)',
        'unit': 'Hz',
    },
    # To get CPU usage percentage in Prometheus, you can use the
    # node_cpu_seconds_total metric, which provides a counter of CPU usage time.
    # To calculate usage percentage, you can use the following query:
    # avg(irate(node_cpu_seconds_total{mode='idle'}[30s])) * 100
    # This query uses the irate() function to calculate the rate of change of
    # the metric over the last interval (in this case, 30 seconds). Then the
    # avg() function calculates the average rate of change across all node
    # instances (as specified in the metric), selecting only the value of the
    # metric for mode="idle", i.e., unused CPU resources. The resulting value
    # is multiplied by 100 to get the CPU usage percentage.
    'cpu-usage-percentage': {
        'query': "avg(irate(node_cpu_seconds_total{mode='idle'}[30s])) * 100",
        'unit': 'Hz',
    },
    'cpu-counts-cores': {
        'query': 'count(node_cpu_seconds_total{mode=~"system"})',
        'unit': 'Hz',
    },
    'cpu-max-frequency': {
        'query': 'sum(node_cpu_frequency_max_hertz)',
        'unit': 'Hz',
    },
    'size-total': {
        # 'query': 'sum(node_filesystem_size_bytes)',
        # # hard disc
        'query': 'sum(node_filesystem_size_bytes{mountpoint=~"/opt/aero/openvair/data/mnt.*"})',  # NFS  # noqa: E501
        'unit': 'B',
    },
    'size-used': {
        # 'query': 'sum(node_filesystem_size_bytes)-sum(node_filesystem_avail_bytes)',  # hard disc  # noqa: E501, W505
        'query': 'sum(node_filesystem_size_bytes{mountpoint=~"/opt/aero/openvair/data/mnt.*"})'  # NFS + localfs  # noqa: E501
        '-sum(node_filesystem_avail_bytes{mountpoint=~"/opt/aero/openvair/data/mnt.*"})',
        'unit': 'B',
    },
    'size-free': {
        # 'query': 'sum(node_filesystem_avail_bytes)',# hard disc
        'query': 'sum(node_filesystem_avail_bytes{mountpoint=~"/opt/aero/openvair/data/mnt.*"})',  # NFS + localfs  # noqa: E501
        'unit': 'B',
    },
    'size-free-system': {
        'query': 'node_filesystem_avail_bytes{mountpoint=~"/"}',
        'unit': 'B',
    },
    'size-system': {
        'query': 'node_filesystem_size_bytes{mountpoint=~"/"}',
        'unit': 'B',
    },
}
