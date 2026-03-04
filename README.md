# PerfTest - Performance Testing Tool

Performance testing tool for video streaming services with Victoria Metrics integration.

## Features

- Send start requests to test endpoints with custom configuration
- Collect metrics from Victoria Metrics (streaming & system metrics)
- Display beautiful console output with metrics summary
- Support for multiple cameras in a single test
- Async HTTP client with retry logic

## Installation

```bash
# Clone the repository
cd perftest

# Install dependencies
pip install -r requirements.txt

# Or install in development mode
pip install -e .
```

## Configuration

Create a YAML configuration file based on the example:

```bash
cp configs/streaming_test.yaml.example configs/streaming_test.yaml
```

Edit `configs/streaming_test.yaml` with your settings:

```yaml
name: "Streaming Performance Test"
test_endpoint_url: "http://localhost:8080/v1/test/run"

start_request:
  duration_seconds: 60
  config:
    streamer:
      stream_server_url: "https://your-sfu-server.com"
      stream_server_key: "your_key"
      stream_server_secret: "your_secret"
    recorder:
      video_chunk_duration_seconds: 10
  cameras:
    - camera_id: 1
      rtsp_url: "rtsp://username:password@camera-ip:port/stream"
      room_name: "test-room-1"
      stream: true
      record: false
      audio: false
      width: 1920
      height: 1080

victoria_metrics:
  url: "http://localhost:8428"
  timeout: 10

output:
  format: "console"
  show_summary: true
```

## Usage

Run a performance test:

```bash
# Basic usage
python -m perftest configs/streaming_test.yaml

# With custom log level
python -m perftest configs/streaming_test.yaml --log-level DEBUG

# Save results to file (future feature)
python -m perftest configs/streaming_test.yaml --output results.json
```

Or use the CLI command if installed:

```bash
perftest configs/streaming_test.yaml
```

## How It Works

1. **Start Request**: Sends POST request to test endpoint with configuration
2. **Wait**: Waits for test duration (duration_seconds + 5s buffer)
3. **Collect Metrics**: Queries Victoria Metrics for the test period
4. **Display Summary**: Shows metrics table with min/avg/max values

## Metrics Collected

### Streaming Metrics
- **Bitrate (Mbps)**: Average bitrate during the test
- **RTT (ms)**: Round-trip time
- **Quality**: Stream quality indicator
- **Score**: Overall quality score

### System Metrics
- **CPU (%)**: CPU usage percentage
- **RAM (%)**: RAM usage percentage
- **RAM (MB)**: RAM usage in megabytes

## Example Output

```
╭─────────────────── Test Results ───────────────────╮
│ Streaming Performance Test                         │
│ Duration: 65.23s                                   │
│ Start: 2024-03-04 10:15:30                        │
│ End: 2024-03-04 10:16:35                          │
╰────────────────────────────────────────────────────╯

          Metrics Summary
┏━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━┳━━━━━━┳━━━━━━┓
┃ Metric       ┃ Samples┃ Min  ┃ Avg  ┃ Max  ┃
┡━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━╇━━━━━━╇━━━━━━┩
│ Bitrate (Mbps)│   12   │ 2.34 │ 2.56 │ 2.89 │
│ RTT (ms)      │   12   │ 34.2 │ 45.6 │ 58.1 │
│ Quality       │   12   │ 1.00 │ 2.00 │ 2.00 │
│ Score         │   12   │ 0.85 │ 0.92 │ 0.98 │
│ CPU (%)       │   12   │ 15.3 │ 25.7 │ 35.2 │
│ RAM (%)       │   12   │ 45.2 │ 52.3 │ 58.9 │
│ RAM (MB)      │   12   │ 4096 │ 4732 │ 5324 │
└──────────────┴────────┴──────┴──────┴──────┘
```

## Architecture

```
perftest/
├── perftest/
│   ├── core/           # Configuration and logging
│   ├── models/         # Pydantic models
│   ├── clients/        # HTTP and Victoria Metrics clients
│   ├── collectors/     # Metrics collection logic
│   ├── services/       # Test runner orchestration
│   ├── formatters/     # Output formatting
│   └── utils/          # Utilities and errors
├── configs/            # Configuration files
└── tests/              # Tests
```

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run linter
ruff check perftest/

# Format code
ruff format perftest/

# Run tests (when available)
pytest
```

## Future Enhancements

- [ ] Recording metrics support
- [ ] Event recording metrics
- [ ] JSON/CSV output formats
- [ ] Historical comparison
- [ ] Performance degradation detection
- [ ] Alert thresholds
- [ ] Web dashboard

## License

Proprietary
