"""Client for querying Victoria Metrics."""

from datetime import datetime
from typing import Any, Dict, Optional

import httpx

from perftest.core.logger import LogStore
from perftest.utils.errors import MetricsQueryError


class VictoriaMetricsClient:
    """Client for querying Victoria Metrics using PromQL."""

    def __init__(
        self,
        base_url: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        timeout: int = 10,
    ):
        """Initialize Victoria Metrics client.

        Args:
            base_url: Base URL of Victoria Metrics (e.g., http://localhost:8428)
            username: Optional username for authentication
            password: Optional password for authentication
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.auth = (username, password) if username and password else None
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        """Enter async context manager."""
        self._client = httpx.AsyncClient(timeout=httpx.Timeout(self.timeout), auth=self.auth)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit async context manager."""
        if self._client:
            await self._client.aclose()

    async def query(self, query: str, time: Optional[datetime] = None) -> Dict[str, Any]:
        """Execute instant PromQL query.

        Args:
            query: PromQL query string
            time: Optional time for query evaluation

        Returns:
            Query result data

        Raises:
            MetricsQueryError: If query fails
        """
        url = f"{self.base_url}/api/v1/query"
        params = {"query": query}

        if time:
            params["time"] = int(time.timestamp())

        try:
            LogStore.metrics.debug(f"Querying: {query}")
            response = await self._client.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            if data.get("status") != "success":
                raise MetricsQueryError(f"Query failed: {data.get('error')}")

            return data.get("data", {})

        except httpx.HTTPStatusError as e:
            raise MetricsQueryError(f"HTTP error: {e}")
        except Exception as e:
            raise MetricsQueryError(f"Query failed: {e}")

    async def query_range(
        self, query: str, start: datetime, end: datetime, step: str = "15s"
    ) -> Dict[str, Any]:
        """Execute range PromQL query.

        Args:
            query: PromQL query string
            start: Start time for query range
            end: End time for query range
            step: Query resolution step (e.g., "15s", "1m")

        Returns:
            Query result data

        Raises:
            MetricsQueryError: If query fails
        """
        url = f"{self.base_url}/api/v1/query_range"
        params = {
            "query": query,
            "start": int(start.timestamp()),
            "end": int(end.timestamp()),
            "step": step,
        }

        try:
            LogStore.metrics.debug(f"Range query: {query} from {start} to {end}")
            response = await self._client.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            if data.get("status") != "success":
                raise MetricsQueryError(f"Range query failed: {data.get('error')}")

            return data.get("data", {})

        except httpx.HTTPStatusError as e:
            raise MetricsQueryError(f"HTTP error: {e}")
        except Exception as e:
            raise MetricsQueryError(f"Range query failed: {e}")
