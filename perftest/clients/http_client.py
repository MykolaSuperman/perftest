"""Async HTTP client with retry and timeout handling."""

from typing import Any, Dict, Optional

import httpx

from perftest.core.logger import LogStore
from perftest.utils.errors import HttpClientError


class AsyncHttpClient:
    """Async HTTP client with retry and timeout handling."""

    def __init__(self, timeout: int = 30, retry_count: int = 3):
        """Initialize HTTP client.

        Args:
            timeout: Request timeout in seconds
            retry_count: Number of retry attempts
        """
        self.timeout = timeout
        self.retry_count = retry_count
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        """Enter async context manager."""
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(self.timeout), follow_redirects=True
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit async context manager."""
        if self._client:
            await self._client.aclose()

    async def request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make HTTP request with retry logic.

        Args:
            method: HTTP method (GET, POST, etc.)
            url: Request URL
            headers: Optional headers dict
            json_data: Optional JSON body

        Returns:
            Response JSON data

        Raises:
            HttpClientError: If request fails after all retries
        """
        for attempt in range(self.retry_count):
            try:
                LogStore.http.info(f"Request {method} {url} (attempt {attempt + 1})")

                response = await self._client.request(
                    method=method, url=url, headers=headers, json=json_data
                )

                response.raise_for_status()

                LogStore.http.info(f"Response {response.status_code}")
                return response.json() if response.content else {}

            except httpx.HTTPStatusError as e:
                LogStore.http.error(f"HTTP error {e.response.status_code}: {e}")
                if attempt == self.retry_count - 1:
                    raise HttpClientError(f"HTTP request failed: {e}")
            except httpx.TimeoutException as e:
                LogStore.http.error(f"Timeout: {e}")
                if attempt == self.retry_count - 1:
                    raise HttpClientError(f"Request timeout: {e}")
            except Exception as e:
                LogStore.http.error(f"Unexpected error: {e}")
                if attempt == self.retry_count - 1:
                    raise HttpClientError(f"Request failed: {e}")
