"""Pydantic models for metrics and results."""

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel


class MetricDataPoint(BaseModel):
    """Single metric data point."""

    timestamp: datetime
    value: float
    labels: Dict[str, str] = {}


class MetricResult(BaseModel):
    """Result of a metric query."""

    name: str
    query: str
    data_points: List[MetricDataPoint]

    def get_values(self) -> List[float]:
        """Extract all values from data points.

        Returns:
            List of metric values
        """
        return [dp.value for dp in self.data_points]

    def get_average(self) -> Optional[float]:
        """Calculate average value across all data points.

        Returns:
            Average value or None if no data points
        """
        values = self.get_values()
        return sum(values) / len(values) if values else None

    def get_min(self) -> Optional[float]:
        """Get minimum value across all data points.

        Returns:
            Minimum value or None if no data points
        """
        values = self.get_values()
        return min(values) if values else None

    def get_max(self) -> Optional[float]:
        """Get maximum value across all data points.

        Returns:
            Maximum value or None if no data points
        """
        values = self.get_values()
        return max(values) if values else None


class TestResult(BaseModel):
    """Complete test execution result."""

    test_name: str
    start_time: datetime
    end_time: datetime
    duration_seconds: float
    metrics: List[MetricResult]
    errors: List[str] = []
