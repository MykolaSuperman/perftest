"""Console output formatter using Rich library."""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from perftest.models.metrics import TestResult


class ConsoleFormatter:
    """Format test results for console output using Rich."""

    def __init__(self):
        """Initialize console formatter."""
        self.console = Console()

    def format_summary(self, result: TestResult):
        """Display test summary with metrics table.

        Args:
            result: Test result with metrics data
        """
        # Header panel
        self.console.print(
            Panel(
                f"[bold cyan]{result.test_name}[/bold cyan]\n"
                f"Duration: {result.duration_seconds:.2f}s\n"
                f"Start: {result.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"End: {result.end_time.strftime('%Y-%m-%d %H:%M:%S')}",
                title="Test Results",
                border_style="cyan",
            )
        )

        # Metrics table
        table = Table(
            title="Metrics Summary", show_header=True, header_style="bold magenta"
        )
        table.add_column("Metric", style="cyan", width=20)
        table.add_column("Samples", justify="right", style="white")
        table.add_column("Min", justify="right", style="green")
        table.add_column("Avg", justify="right", style="yellow")
        table.add_column("Max", justify="right", style="red")

        for metric in result.metrics:
            samples = len(metric.data_points)
            min_val = metric.get_min()
            avg_val = metric.get_average()
            max_val = metric.get_max()

            table.add_row(
                metric.name,
                str(samples),
                f"{min_val:.2f}" if min_val is not None else "N/A",
                f"{avg_val:.2f}" if avg_val is not None else "N/A",
                f"{max_val:.2f}" if max_val is not None else "N/A",
            )

        self.console.print(table)

        # Errors panel (if any)
        if result.errors:
            error_text = Text("\n".join(result.errors), style="bold red")
            self.console.print(Panel(error_text, title="Errors", border_style="red"))
