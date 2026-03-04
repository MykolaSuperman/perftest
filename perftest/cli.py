"""CLI interface for perftest application."""

import asyncio

import click

from perftest.core.config import Settings
from perftest.formatters.console import ConsoleFormatter
from perftest.services.test_runner import TestRunner


@click.command()
@click.argument("config_file", type=click.Path(exists=True))
@click.option("--log-level", default="INFO", help="Log level (DEBUG, INFO, WARNING, ERROR)")
@click.option("--output", "-o", type=click.Path(), help="Save results to file")
def run_test(config_file: str, log_level: str, output: str):
    """Run performance test with the given configuration.

    CONFIG_FILE: Path to YAML configuration file
    """
    # Load configuration
    config = Settings.load_test_config(config_file)

    # Override output if provided
    if output:
        config.output.save_to_file = output

    # Run test
    result = asyncio.run(_execute_test(config))

    # Format and display output
    formatter = ConsoleFormatter()
    formatter.format_summary(result)


async def _execute_test(config):
    """Execute test asynchronously.

    Args:
        config: Test configuration

    Returns:
        Test result
    """
    runner = TestRunner(config)
    return await runner.run()


if __name__ == "__main__":
    run_test()
