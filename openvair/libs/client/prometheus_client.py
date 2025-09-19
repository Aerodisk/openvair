"""Prometheus client module.

This module defines the `PrometheusClient` class, which provides methods
for interacting with the Prometheus monitoring service. It includes methods
for querying metrics and retrieving node information from Prometheus.

Classes:
    PrometheusClient: A client class for interacting with the Prometheus API.
"""


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

    def get_prometheus_data(self, query: str) -> dict:
        """Retrieve data from Prometheus based on the specified query option.

        Args:
            query (str): The query to be used in the Prometheus API call.

        Returns:
            Dict: The JSON response from Prometheus as a dictionary.
        """
        query_url = f'{self.source_url}/api/v1/query?query={query}'
        result = self.session.get(query_url, verify=False)
        return result.json()

    def ping(self) -> None:
        """Ping the Prometheus service to check its availability.

        This method sends a simple GET request to the Prometheus service URL
        to verify its availability.

        Returns:
            Dict: The response from Prometheus, typically the status or health
                check data.
        """
        self.session.get(self.source_url, verify=False)

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

        node_info_values_sum = 0.0
        try:
            query_result = self.get_prometheus_data(
                PROMETHEUS_QUERIES[option]['query']
            )

            data_result: list[dict] = query_result['data']['result']
            for row in data_result:
                node_info_values_sum += float(row['value'][1])
        except (KeyError, RequestException) as err:
            LOG.warning(err)
            LOG.warning(
                f'Failed to get node info from Prometheus with option: {option}'
            )
            LOG.error('Prometheus API request failed.')
            return 0.0
        else:
            LOG.info('Finished getting node info from Prometheus successfully.')
            return node_info_values_sum
