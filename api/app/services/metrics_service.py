import logging

from pydantic import BaseModel

from app.constants import DockerComposeLabel
from app.services.docker_client import get_all_containers_for_project
import docker
import docker.errors
import docker.models.containers


_logger = logging.getLogger(__name__)
_BYTES_PER_MB: int = 1024 * 1024
_BLKIO_OP_READ: str = "Read"
_BLKIO_OP_WRITE: str = "Write"


class ServiceMetrics(BaseModel):
    """Resource usage snapshot for a single Compose service container."""

    service: str
    container_id: str
    status: str
    cpu_percent: float
    mem_usage_mb: float
    mem_limit_mb: float
    mem_percent: float
    net_rx_mb: float
    net_tx_mb: float
    block_read_mb: float
    block_write_mb: float


class MetricsService:
    """Collects real-time resource metrics from Docker containers."""

    @staticmethod
    def _bytes_to_mb(byte_count: int) -> float:
        """Convert a byte count to megabytes, rounded to 2 decimal places."""
        return round(byte_count / _BYTES_PER_MB, 2)

    @staticmethod
    def _calc_cpu_percent(stats: dict) -> float:
        """Compute CPU usage percentage from raw Docker stats, or 0.0 on missing data."""
        cpu_stats = stats.get("cpu_stats", {})
        precpu_stats = stats.get("precpu_stats", {})
        cpu_delta = cpu_stats.get("cpu_usage", {}).get("total_usage", 0) - precpu_stats.get("cpu_usage", {}).get(
            "total_usage", 0
        )
        system_delta = cpu_stats.get("system_cpu_usage", 0) - precpu_stats.get("system_cpu_usage", 0)
        nb_cpus: int = cpu_stats.get("online_cpus") or len(cpu_stats.get("cpu_usage", {}).get("percpu_usage", [None]))
        if system_delta <= 0 or nb_cpus <= 0:
            return 0.0
        return (cpu_delta / system_delta) * nb_cpus * 100.0

    def _parse_stats(self, container: docker.models.containers.Container, stats: dict) -> ServiceMetrics:
        """Build a ServiceMetrics instance from raw Docker stats."""
        service_name: str = container.labels.get(DockerComposeLabel.SERVICE, container.name)
        mem: dict = stats.get("memory_stats", {})
        mem_limit: int = max(mem.get("limit", 1), 1)

        network_rx_bytes = network_tx_bytes = 0.0
        for network_interface in stats.get("networks", {}).values():
            network_rx_bytes += network_interface.get("rx_bytes", 0)
            network_tx_bytes += network_interface.get("tx_bytes", 0)

        block_read_bytes = block_write_bytes = 0
        for block_stat in stats.get("blkio_stats", {}).get("io_service_bytes_recursive") or []:
            if block_stat.get("op") == _BLKIO_OP_READ:
                block_read_bytes += block_stat.get("value", 0)
            elif block_stat.get("op") == _BLKIO_OP_WRITE:
                block_write_bytes += block_stat.get("value", 0)

        return ServiceMetrics(
            service=service_name,
            container_id=container.short_id,
            status=container.status,
            cpu_percent=round(self._calc_cpu_percent(stats), 2),
            mem_usage_mb=self._bytes_to_mb(mem.get("usage", 0)),
            mem_limit_mb=self._bytes_to_mb(mem.get("limit", 1)),
            mem_percent=round((mem.get("usage", 0) / mem_limit) * 100, 2),
            net_rx_mb=self._bytes_to_mb(int(network_rx_bytes)),
            net_tx_mb=self._bytes_to_mb(int(network_tx_bytes)),
            block_read_mb=self._bytes_to_mb(block_read_bytes),
            block_write_mb=self._bytes_to_mb(block_write_bytes),
        )

    def _zero_metrics(self, container: docker.models.containers.Container) -> ServiceMetrics:
        """Return zeroed-out ServiceMetrics when stats cannot be retrieved."""
        return ServiceMetrics(
            service=container.labels.get(DockerComposeLabel.SERVICE, container.name),
            container_id=container.short_id,
            status=container.status,
            cpu_percent=0.0,
            mem_usage_mb=0.0,
            mem_limit_mb=0.0,
            mem_percent=0.0,
            net_rx_mb=0.0,
            net_tx_mb=0.0,
            block_read_mb=0.0,
            block_write_mb=0.0,
        )

    def get_project_metrics(self, project_id: str) -> list[ServiceMetrics]:
        """Return resource metrics for all containers in a Compose project."""
        result: list[ServiceMetrics] = []
        for container in get_all_containers_for_project(project_id):
            try:
                raw_stats = container.stats(stream=False)
            except docker.errors.APIError as api_exc:
                _logger.warning(
                    "Could not get stats for container %s: %s",
                    container.short_id,
                    api_exc,
                )
                result.append(self._zero_metrics(container))
            else:
                result.append(self._parse_stats(container, raw_stats))
        return result


metrics_service = MetricsService()
