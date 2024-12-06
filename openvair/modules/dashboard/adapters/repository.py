"""Module for managing node resource data using Prometheus.

This module defines two classes:
    `AbstractRepository` and `PrometheusRepository`.
The `AbstractRepository` class is an abstract base class that defines the
interface for retrieving node resource data. The `PrometheusRepository` class
is a concrete implementation of the `AbstractRepository` that uses the
Prometheus client to retrieve the data.

The `PrometheusRepository` class provides methods to retrieve various types of
node resource data, including CPU, memory, storage, IOPS, latency, network
bandwidth, and disk data. The data is retrieved from the Prometheus client and
returned as a dictionary.

Classes:
    AbstractRepository: An abstract base class for retrieving node resource
        data.
    PrometheusRepository: A concrete implementation of the `AbstractRepository`
        that uses the Prometheus client to retrieve node resource data.
"""

import abc
import time
from typing import Any, Dict

from openvair.libs.log import get_logger
from openvair.libs.client.prometheus_client import PrometheusClient

LOG = get_logger(__name__)


class AbstractRepository(metaclass=abc.ABCMeta):
    """An abstract base class for retrieving node resource data."""

    # prometheus
    def get_data(self) -> Dict:
        """Get node resource data.

        Returns:
            Dict: A dictionary containing the node resource data.
        """
        return self._get_data()

    @abc.abstractmethod
    def _get_data(self) -> Dict:
        """Retrieve node resource data.

        Returns:
            Dict: A dictionary containing the node resource data.
        """
        pass


class PrometheusRepository(AbstractRepository):
    """A concrete implementation of the `AbstractRepository`.

    That uses Prometheus. This class provides methods to retrieve various types
    of node resource data, including CPU, memory, storage, IOPS, latency,
    network bandwidth, and disk data. The data is retrieved from the Prometheus
    client and returned as a dictionary.

    Attributes:
        prometheus_client (PrometheusClient): An instance of the
            PrometheusClient class, used to interact with the Prometheus server.
    """

    def __init__(self) -> None:
        """Initialize the PrometheusRepository object."""
        super().__init__()
        self.prometheus_client = PrometheusClient()

    def _get_cpu_info(self) -> Dict:
        """It gets the number of cores from Prometheus gets the CPU usage info

        Info is a percentage from Prometheus

        Returns:
            A dictionary with the number of cores and the percentage of
                cpu usage.
        """
        LOG.info('Start getting cpu data from node.')
        cores = 0
        cores_prometheus = self.prometheus_client.get_node_info(
            'cpu-counts-cores'
        )
        cores += int(cores_prometheus)
        cpu = {
            'count': cores,
            'percentage': round(
                self.prometheus_client.get_node_info('cpu-usage-percentage'), 2
            ),
        }
        LOG.info('Finished getting cpu data from node.')

        return cpu

    def _get_storage_info(self) -> Dict:
        """Get storage information from the node.

        Returns:
            Dict: A dictionary containing the storage information, including
                total size, used space, free space, and the percentage of
                used space.
        """
        warning_cls_limit = 75
        danger_cls_limit = 90

        LOG.info('Start getting storage info from node.')
        size = self.prometheus_client.get_node_info('size-total')
        if not size:
            size = 0

        storage: Dict[str, Any] = {
            'size': size,
            'used': self.prometheus_client.get_node_info('size-used'),
            'free': self.prometheus_client.get_node_info('size-free'),
        }
        percentage = round(
            (storage['used'] / storage['size'] * 100) if storage['size'] else 0,
            2,
        )
        storage.update(
            {
                'percentage': percentage,
                'free': storage['free'],
                'size': storage['size'],
                'used': storage['used'],
                'cls': 'success'
                if percentage < warning_cls_limit
                else ('warning' if percentage < danger_cls_limit else 'danger'),
            }
        )
        LOG.info('Finished getting storage info from node.')

        return storage

    def _get_memory_info(self) -> Dict:
        """Get and calculate the percentage of memory used.

        It gets the total memory, used memory, and available memory from the
        node, and then calculates the percentage of memory used.

        Returns:
            Dict: A dictionary containing the total memory, used memory,
                available memory, and the percentage of memory used.
        """
        LOG.info('Getting memory info from node.')
        mem = {
            'value': self.prometheus_client.get_node_info('ram-total'),
            'used': self.prometheus_client.get_node_info('ram-used'),
            'available': self.prometheus_client.get_node_info('ram-available'),
            'percentage': 0,
        }

        if mem['value']:
            mem.update(
                {'percentage': round(mem['used'] / mem['value'] * 100, 2)}
            )

        mem.update(
            {
                'value': mem['value'],
                'used': mem['used'],
                'available': mem['available'],
            }
        )
        LOG.info('Finished getting memory info from node.')

        return mem

    def _get_iops_info(self) -> Dict:
        """Get IOPS information from the node.

        Returns:
            Dict: A dictionary containing the read and write IOPS data.
        """
        LOG.info('Getting iops dsta from node.')
        iops_read = {
            'input': int(self.prometheus_client.get_node_info('io-read-ps')),
            'output': int(self.prometheus_client.get_node_info('io-write-ps')),
            'date': round(time.time() * 1000),
        }
        LOG.info('Finished getting iops data from node.')
        return iops_read

    def _get_latency(self) -> Dict:
        """Get latency information from the node.

        Returns:
            Dict: A dictionary containing the latency information.
        """
        LOG.info('Getting iops dsta from node.')
        io_latency = {
            'wait': self.prometheus_client.get_node_info('latency'),
            'date': round(time.time() * 1000),
        }
        LOG.info('Finished getting latency info from node.')
        return io_latency

    def _get_network_bandwidth(self) -> Dict:
        """Get network bandwidth information from the node.

        Returns:
            Dict: A dictionary containing the read and write network bandwidth.
        """
        bandwidth_read = self.prometheus_client.get_node_info('bandwidth-read')
        bandwidth_write = self.prometheus_client.get_node_info(
            'bandwidth-write'
        )
        return {
            'read': bandwidth_read,
            'write': bandwidth_write,
            'date': round(time.time() * 1000),
        }

    def _get_disk_data(self) -> Dict:
        """Get disk metrics from the node.

        This method queries Prometheus for disk metrics such as read and write
        speeds, and returns the obtained data in a dictionary format.

        Returns:
            Dict: A dictionary containing disk metrics, including 'read' and
                'write' speeds in mb per second, and the timestamp of data
                retrieval.
        """
        LOG.info('Start getting disk data from node.')
        disk_data = {
            'read': self.prometheus_client.get_node_info('disk-read'),
            'write': self.prometheus_client.get_node_info('disk-write'),
            'date': round(time.time() * 1000),
        }
        LOG.info('Finished getting disk data from node.')
        return disk_data

    def _get_data(self) -> Dict:
        """Retrieve all node resource data from Prometheus.

        This method retrieves all the node resource data, including CPU, memory,
        storage, IOPS, latency, network bandwidth, and disk data, and returns it
        as a dictionary.

        Returns:
            Dict: A dictionary containing all the node resource data, including:
                - 'cpu': A dictionary with CPU information, including the number
                of cores and the percentage of CPU usage.
                - 'memory': A dictionary with memory information, including the
                total memory, used memory, available memory, and the percentage
                of memory used.
                - 'storage': A dictionary with storage information, including
                the total size, used space, free space, and the percentage of
                used space.
                - 'iops': A dictionary with IOPS information, including the read
                and write IOPS data.
                - 'io_latency': A dictionary with latency information, including
                the I/O wait time.
                - 'bandwith_data': A dictionary with network bandwidth
                information, including the read and write bandwidth.
                - 'disk_data': A dictionary with disk metrics, including the
                read and write speeds in mb per second, and the timestamp of
                data retrieval.
        """
        LOG.info('Start getting full data from node.')
        data = {}

        self.prometheus_client.ping()

        cpu = self._get_cpu_info()
        memory = self._get_memory_info()
        storage = self._get_storage_info()
        iops = self._get_iops_info()
        io_latency = self._get_latency()
        bandwith_data = self._get_network_bandwidth()
        disk_data = self._get_disk_data()
        data.update(
            {
                'cpu': cpu,
                'memory': memory,
                'storage': storage,
                'iops': iops,
                'io_latency': io_latency,
                'bandwith_data': bandwith_data,
                'disk_data': disk_data,
            }
        )
        LOG.info('Finished getting full data from node.')

        return data
