"""Custom exceptions for perftest application."""


class PerfTestError(Exception):
    """Base exception for perftest."""

    pass


class ConfigError(PerfTestError):
    """Configuration related errors."""

    pass


class HttpClientError(PerfTestError):
    """HTTP client errors."""

    pass


class MetricsQueryError(PerfTestError):
    """Metrics query errors."""

    pass
