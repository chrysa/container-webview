import pytest

from app.services.metrics_service import MetricsService


class TestMetricsService:
    """Unit tests for MetricsService."""

    class TestBytesToMb:
        """Tests for _bytes_to_mb()."""

        @pytest.mark.parametrize("byte_count,expected_mb", [
            (0, 0.0),
            (1024 * 1024, 1.0),
            (512 * 1024, 0.49),
            (10 * 1024 * 1024, 10.0),
        ])
        def test_converts_bytes_to_megabytes(self, byte_count, expected_mb):
            """Convert byte count to megabytes, rounded to 2 decimal places.

            Given: A byte count
            When: Calling _bytes_to_mb()
            Then: Should return the correct megabyte value rounded to 2 decimals
            """
            result = MetricsService._bytes_to_mb(byte_count)
            assert result == expected_mb, f"For {byte_count=} expected {expected_mb=} but got {result=}"

    class TestCalcCpuPercent:
        """Tests for _calc_cpu_percent()."""

        def test_returns_zero_when_system_delta_is_zero(self):
            """Return 0.0 when system CPU delta is zero (avoids division by zero).

            Given: CPU stats where system_cpu_usage did not change
            When: Calling _calc_cpu_percent()
            Then: Should return 0.0
            """
            stats = {
                "cpu_stats": {"cpu_usage": {"total_usage": 100}, "system_cpu_usage": 1000, "online_cpus": 2},
                "precpu_stats": {"cpu_usage": {"total_usage": 50}, "system_cpu_usage": 1000},
            }
            result = MetricsService._calc_cpu_percent(stats)
            assert result == 0.0, f"Expected 0.0 but got {result=}"

        def test_calculates_cpu_percent_correctly(self):
            """Calculate CPU percentage from valid CPU stats.

            Given: Stats with a measurable CPU and system delta and 2 CPUs
            When: Calling _calc_cpu_percent()
            Then: Should return a non-zero float percentage
            """
            stats = {
                "cpu_stats": {
                    "cpu_usage": {"total_usage": 200_000_000},
                    "system_cpu_usage": 2_000_000_000,
                    "online_cpus": 2,
                },
                "precpu_stats": {
                    "cpu_usage": {"total_usage": 100_000_000},
                    "system_cpu_usage": 1_000_000_000,
                },
            }
            result = MetricsService._calc_cpu_percent(stats)
            assert result > 0.0, f"Expected positive CPU percent but got {result=}"
            assert result <= 200.0, f"CPU percent should be ≤ 200% (2 CPUs) but got {result=}"

        def test_returns_zero_with_empty_stats(self):
            """Return 0.0 when stats dict is empty.

            Given: An empty stats dictionary
            When: Calling _calc_cpu_percent()
            Then: Should return 0.0 without raising
            """
            result = MetricsService._calc_cpu_percent({})
            assert result == 0.0, f"Expected 0.0 but got {result=}"

    class TestParseStats:
        """Tests for _parse_stats()."""

        def test_builds_service_metrics_from_stats(self, mocker):
            """Build ServiceMetrics from raw Docker stats.

            Given: A container mock with labels and a realistic stats payload
            When: Calling _parse_stats()
            Then: Should return a ServiceMetrics with correct values
            """
            container = mocker.MagicMock()
            container.short_id = "abc123"
            container.status = "running"
            container.labels = {"com.docker.compose.service": "web"}
            container.name = "project_web_1"

            stats = {
                "cpu_stats": {
                    "cpu_usage": {"total_usage": 200_000_000},
                    "system_cpu_usage": 2_000_000_000,
                    "online_cpus": 2,
                },
                "precpu_stats": {
                    "cpu_usage": {"total_usage": 100_000_000},
                    "system_cpu_usage": 1_000_000_000,
                },
                "memory_stats": {"usage": 50 * 1024 * 1024, "limit": 512 * 1024 * 1024},
                "networks": {
                    "eth0": {"rx_bytes": 1024 * 1024, "tx_bytes": 512 * 1024},
                },
                "blkio_stats": {"io_service_bytes_recursive": [
                    {"op": "Read", "value": 2 * 1024 * 1024},
                    {"op": "Write", "value": 1 * 1024 * 1024},
                ]},
            }

            service = MetricsService()
            result = service._parse_stats(container, stats)

            assert result.service == "web", f"Expected 'web' but got {result.service=}"
            assert result.container_id == "abc123", f"Expected 'abc123' but got {result.container_id=}"
            assert result.status == "running", f"Expected 'running' but got {result.status=}"
            assert result.cpu_percent > 0.0, f"Expected positive CPU percent but got {result.cpu_percent=}"
            assert result.mem_usage_mb == 50.0, f"Expected 50.0 MB but got {result.mem_usage_mb=}"
            assert result.net_rx_mb == 1.0, f"Expected 1.0 MB rx but got {result.net_rx_mb=}"
            assert result.block_read_mb == 2.0, f"Expected 2.0 MB read but got {result.block_read_mb=}"
            assert result.block_write_mb == 1.0, f"Expected 1.0 MB write but got {result.block_write_mb=}"

    class TestGetProjectMetrics:
        """Tests for get_project_metrics()."""

        def test_returns_metrics_for_all_project_containers(self, mocker):
            """Return one ServiceMetrics per container in the project.

            Given: A project with 2 containers that return valid stats
            When: Calling get_project_metrics("myproject")
            Then: Should return a list of 2 ServiceMetrics
            """
            c1 = mocker.MagicMock()
            c1.short_id = "aaa"
            c1.status = "running"
            c1.labels = {"com.docker.compose.service": "web"}
            c1.stats.return_value = {
                "cpu_stats": {"cpu_usage": {"total_usage": 0}, "system_cpu_usage": 0, "online_cpus": 1},
                "precpu_stats": {"cpu_usage": {"total_usage": 0}, "system_cpu_usage": 0},
                "memory_stats": {"usage": 0, "limit": 1},
                "networks": {},
                "blkio_stats": {"io_service_bytes_recursive": []},
            }

            c2 = mocker.MagicMock()
            c2.short_id = "bbb"
            c2.status = "running"
            c2.labels = {"com.docker.compose.service": "db"}
            c2.stats.return_value = c1.stats.return_value

            mocker.patch(
                "app.services.metrics_service.docker_client.get_all_containers_for_project",
                return_value=[c1, c2],
            )

            service = MetricsService()
            result = service.get_project_metrics("myproject")

            assert len(result) == 2, f"Expected 2 metrics but got {len(result)=}"

        def test_returns_zeroed_metrics_on_api_error(self, mocker):
            """Return zeroed-out metrics when Docker stats API raises APIError.

            Given: A container that raises docker.errors.APIError on stats()
            When: Calling get_project_metrics()
            Then: Should return zeroed ServiceMetrics instead of raising
            """
            import docker.errors

            container = mocker.MagicMock()
            container.short_id = "abc"
            container.status = "running"
            container.labels = {"com.docker.compose.service": "web"}
            container.stats.side_effect = docker.errors.APIError("stats failed")

            mocker.patch(
                "app.services.metrics_service.docker_client.get_all_containers_for_project",
                return_value=[container],
            )

            service = MetricsService()
            result = service.get_project_metrics("myproject")

            assert len(result) == 1, f"Expected 1 result but got {len(result)=}"
            assert result[0].cpu_percent == 0.0, f"Expected 0.0 cpu but got {result[0].cpu_percent=}"
            assert result[0].mem_usage_mb == 0.0, f"Expected 0.0 mem but got {result[0].mem_usage_mb=}"
