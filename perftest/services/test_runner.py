"""Test runner service for orchestrating performance tests."""

import asyncio
from datetime import datetime

from perftest.clients.http_client import AsyncHttpClient
from perftest.collectors.metrics_collector import MetricsCollector
from perftest.core.logger import LogStore
from perftest.models.config import TestConfig
from perftest.models.metrics import TestResult


class TestRunner:
    """Orchestrates the complete test execution flow."""

    def __init__(self, config: TestConfig):
        """Initialize test runner.

        Args:
            config: Complete test configuration
        """
        self.config = config

    async def run(self) -> TestResult:
        """Execute the complete test flow.

        Flow:
        1. Record start time
        2. Send start request to test endpoint
        3. Wait for test duration (with buffer)
        4. Record end time
        5. Collect metrics from Victoria Metrics
        6. Return test result

        Returns:
            TestResult with metrics and errors
        """
        start_time = datetime.now()
        errors = []
        metrics = []

        try:
            # Step 1: Send start request
            LogStore.test.info(f"Starting test: {self.config.name}")
            await self._send_start_request()

            # Step 2: Wait for test duration (add 5 second buffer)
            duration = self.config.start_request.duration_seconds
            LogStore.test.info(f"Waiting for test to complete ({duration}s + 5s buffer)...")
            await asyncio.sleep(duration + 5)

            # Step 3: Record end time
            end_time = datetime.now()

            # Step 4: Collect metrics from Victoria Metrics
            LogStore.test.info("Collecting metrics from Victoria Metrics...")
            collector = MetricsCollector(self.config.victoria_metrics)
            metrics = await collector.collect_range(start_time, end_time)

            LogStore.test.info(f"Test completed. Collected {len(metrics)} metrics.")

        except Exception as e:
            LogStore.test.error(f"Test execution failed: {e}")
            errors.append(str(e))
            end_time = datetime.now()

        duration_seconds = (end_time - start_time).total_seconds()

        return TestResult(
            test_name=self.config.name,
            start_time=start_time,
            end_time=end_time,
            duration_seconds=duration_seconds,
            metrics=metrics,
            errors=errors,
        )

    async def _send_start_request(self):
        """Send the initial HTTP request to start the test."""
        # Prepare request body
        body = {
            "duration_seconds": self.config.start_request.duration_seconds,
            "config": {
                "streamer": {
                    "stream_server_url": self.config.start_request.config.streamer.stream_server_url,
                    "stream_server_key": self.config.start_request.config.streamer.stream_server_key,
                    "stream_server_secret": self.config.start_request.config.streamer.stream_server_secret,
                },
                "recorder": {
                    "video_chunk_duration_seconds": self.config.start_request.config.recorder.video_chunk_duration_seconds,
                },
            },
            "cameras": [
                {
                    "camera_id": camera.camera_id,
                    "rtsp_url": camera.rtsp_url,
                    "room_name": camera.room_name,
                    "stream": camera.stream,
                    "record": camera.record,
                    "audio": camera.audio,
                    "width": camera.width,
                    "height": camera.height,
                }
                for camera in self.config.start_request.cameras
            ],
        }

        async with AsyncHttpClient() as client:
            response = await client.request(
                method="POST",
                url=self.config.test_endpoint_url,
                headers={"Content-Type": "application/json"},
                json_data=body,
            )

            LogStore.test.info(f"Start request successful: {response}")
