"""Metrics collector for Victoria Metrics."""

from datetime import datetime
from typing import Dict, List, Optional

from perftest.clients.victoria_metrics import VictoriaMetricsClient
from perftest.core.logger import LogStore
from perftest.models.config import VictoriaMetricsConfig
from perftest.models.metrics import MetricDataPoint, MetricResult


class MetricsCollector:
    """Collects streaming and system metrics from Victoria Metrics.

    Hardcoded queries based on vehicle-video metrics format:
    - streaming measurement: bitrate_mbps, rtt_ms, quality, score
    - system measurement: cpu_percent, ram_percent, ram_mb
    """

    # Hardcoded PromQL queries for streaming and system metrics
    QUERIES = {
        # Streaming metrics
        "Bitrate (Mbps)": 'streaming_bitrate_mbps',
        "RTT (ms)": 'streaming_rtt_ms',
        "Quality": 'streaming_quality',
        "Score": 'streaming_score',
        # System metrics
        "CPU (%)": 'system_cpu_percent',
        "RAM (%)": 'system_ram_percent',
        "RAM (MB)": 'system_ram_mb',
    }

    def __init__(self, config: VictoriaMetricsConfig):
        """Initialize metrics collector.

        Args:
            config: Victoria Metrics configuration
        """
        self.config = config
        self.client: Optional[VictoriaMetricsClient] = None

    async def collect_range(
        self, start_time: datetime, end_time: datetime, step: str = "5s"
    ) -> List[MetricResult]:
        """Collect metrics for the given time range.

        Args:
            start_time: Start of the time range
            end_time: End of the time range
            step: Query resolution step (default: 5s)

        Returns:
            List of metric results
        """
        results = []

        async with VictoriaMetricsClient(
            base_url=self.config.url,
            username=self.config.username,
            password=self.config.password,
            timeout=self.config.timeout,
        ) as client:
            for metric_name, query in self.QUERIES.items():
                try:
                    LogStore.metrics.info(f"Collecting metric: {metric_name}")
                    data = await client.query_range(query, start_time, end_time, step)
                    result = self._parse_query_result(metric_name, query, data)
                    results.append(result)
                    LogStore.metrics.info(
                        f"Collected {len(result.data_points)} data points for {metric_name}"
                    )

                except Exception as e:
                    LogStore.metrics.error(f"Failed to collect metric '{metric_name}': {e}")
                    # Add empty result for failed metric
                    results.append(
                        MetricResult(name=metric_name, query=query, data_points=[])
                    )

        return results

    def _parse_query_result(
        self, metric_name: str, query: str, data: Dict
    ) -> MetricResult:
        """Parse Victoria Metrics query result into MetricResult.

        Args:
            metric_name: Name of the metric
            query: PromQL query string
            data: Victoria Metrics response data

        Returns:
            Parsed metric result
        """
        # Victoria Metrics returns: {"resultType": "matrix", "result": [...]}
        results = data.get("result", [])
        data_points = []

        for item in results:
            metric_labels = item.get("metric", {})
            values = item.get("values", [])

            # values is list of [timestamp, value_string]
            for value_pair in values:
                if len(value_pair) >= 2:
                    timestamp = datetime.fromtimestamp(float(value_pair[0]))
                    value = float(value_pair[1])

                    data_point = MetricDataPoint(
                        timestamp=timestamp, value=value, labels=metric_labels
                    )
                    data_points.append(data_point)

        return MetricResult(name=metric_name, query=query, data_points=data_points)
