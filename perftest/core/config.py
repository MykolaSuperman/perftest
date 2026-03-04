"""Configuration management for perftest application."""

import pathlib
from typing import Any

import yaml

from perftest.utils.errors import ConfigError


class Settings:
    """Global application settings."""

    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "structured"  # structured, simple
    TIMEOUT: int = 30
    RETRY_COUNT: int = 3

    @staticmethod
    def load_test_config(config_path: str) -> Any:
        """Load test configuration from YAML file.

        Args:
            config_path: Path to YAML configuration file

        Returns:
            TestConfig object with validated configuration

        Raises:
            ConfigError: If file not found or invalid YAML
        """
        path = pathlib.Path(config_path)
        if not path.exists():
            raise ConfigError(f"Config file not found: {config_path}")

        try:
            with open(path, "r") as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ConfigError(f"Invalid YAML in config file: {e}")

        # Import here to avoid circular dependency
        from perftest.models.config import TestConfig

        try:
            return TestConfig(**data)
        except Exception as e:
            raise ConfigError(f"Invalid configuration: {e}")


settings = Settings()
