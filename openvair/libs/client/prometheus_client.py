"""Prometheus client module.

This module defines the `PrometheusClient` class, which provides methods
for interacting with the Prometheus monitoring service. It includes methods
for querying metrics and retrieving node information from Prometheus.

Classes:
    PrometheusClient: A client class for interacting with the Prometheus API.
"""

from typing import Dict

from requests import RequestException

from openvair.libs.log import get_logger
from openvair.libs.client.config import PROMETHEUS_QUERIES
from openvair.libs.client.base_client import PrometheusBaseClient

LOG = get_logger(__name__)


class PrometheusClient(PrometheusBaseClient):
    """A client class for interacting with the Prometheus API.

    This class provides methods to query data from Prometheus and retrieve
    specific node information based on predefined metrics.
    """

    def get_prometheus_data(self, option: str) -> Dict:
        """Retrieve data from Prometheus based on the specified query option.

        Args:
            option (str): The query option to be used in the Prometheus API
                call.

        Returns:
            Dict: The JSON response from Prometheus as a dictionary.
        """
        option_url = f'{self.source_url}/api/v1/query?query={option}'
        result = self.session.get(option_url, verify=False)
        return result.json()

    def ping(self) -> Dict:
        """Ping the Prometheus service to check its availability.

        This method sends a simple GET request to the Prometheus service URL
        to verify its availability.

        Returns:
            Dict: The response from Prometheus, typically the status or health
                check data.
        """
        return self.session.get(self.source_url, verify=False)

    def request_to_prometheus_for_query(self, query: str) -> float:
        """Send a query request to Prometheus and sum the results.

        This method sends a request to the Prometheus service using the provided
        query string. It then sums up the values of the returned metric rows.

        Args:
            query (str): The Prometheus query string.

        Returns:
            float: The sum of the metric rows returned by the query.
        """
        LOG.info(f'Start Prometheus API request with query: {query}')
        try:
            result = 0.0

            data = self.get_prometheus_data(query)['data']['result']
            for row in data:
                result += float(row['value'][1])

            LOG.info('Finished Prometheus API request.')
        except RequestException:
            LOG.error('Prometheus API request failed.')
            return 0.0
        else:
            return result

    def get_node_info(self, option: str) -> float:
        """Retrieve node information from Prometheus based on a metric name.

        This method fetches node information from Prometheus using a predefined
        metric query. It returns the result of the query as a float.

        Args:
            option (str): The metric name for which to retrieve node
                information.

        Returns:
            float: The result of the Prometheus query, or 0.0 if the query
                fails.
        """
        LOG.info(f'Start getting node info from Prometheus. Option: {option}')
        query = PROMETHEUS_QUERIES.get(option, '')

        if not query:
            LOG.warning(
                f'Failed to get node info from Prometheus with option: {option}'
            )
            return 0.0

        if option in ['io-write-ps', 'io-read-ps']:
            kname = '???'
            response = self.request_to_prometheus_for_query(
                query['query'].format(kname)
            )
        else:
            response = self.request_to_prometheus_for_query(query['query'])

        LOG.info('Finished getting node info from Prometheus successfully.')

        return response if response else 0.0
