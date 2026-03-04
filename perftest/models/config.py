"""Pydantic models for configuration validation."""

from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl


class StreamerConfig(BaseModel):
    """Configuration for the streamer service."""

    stream_server_url: str
    stream_server_key: str
    stream_server_secret: str


class RecorderConfig(BaseModel):
    """Configuration for the recorder service."""

    video_chunk_duration_seconds: int


class ServiceConfig(BaseModel):
    """Combined service configuration."""

    streamer: StreamerConfig
    recorder: RecorderConfig


class CameraConfig(BaseModel):
    """Configuration for a single camera."""

    camera_id: int
    rtsp_url: str
    room_name: str
    stream: bool
    record: bool
    audio: bool
    width: int
    height: int


class StartRequestConfig(BaseModel):
    """Configuration for the test start request."""

    duration_seconds: int
    config: ServiceConfig
    cameras: List[CameraConfig]


class VictoriaMetricsConfig(BaseModel):
    """Configuration for Victoria Metrics connection."""

    url: str  # Full URL with port (e.g., http://localhost:8428)
    timeout: int = 10
    username: Optional[str] = None
    password: Optional[str] = None


class OutputConfig(BaseModel):
    """Configuration for output formatting."""

    format: str = "console"  # console, json, csv
    show_summary: bool = True
    show_detailed: bool = False
    save_to_file: Optional[str] = None


class TestConfig(BaseModel):
    """Complete test configuration."""

    name: str
    description: Optional[str] = None
    test_endpoint_url: str
    start_request: StartRequestConfig
    victoria_metrics: VictoriaMetricsConfig
    output: OutputConfig = Field(default_factory=OutputConfig)
