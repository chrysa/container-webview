from pydantic import BaseModel

from app.constants import COMPOSE_LABEL_SERVICE
from app.services.docker_client import docker_client

_BYTES_PER_MB: int = 1024 * 1024
_BLKIO_OP_READ: str = "Read"
_BLKIO_OP_WRITE: str = "Write"


class ServiceMetrics(BaseModel):
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
    @staticmethod
    def _bytes_to_mb(b: int) -> float:
        return round(b / _BYTES_PER_MB, 2)

    @staticmethod
    def _calc_cpu_percent(stats: dict) -> float:
        try:
            cpu_delta = (
                stats["cpu_stats"]["cpu_usage"]["total_usage"]
                - stats["precpu_stats"]["cpu_usage"]["total_usage"]
            )
            system_delta = (
                stats["cpu_stats"]["system_cpu_usage"]
                - stats["precpu_stats"]["system_cpu_usage"]
            )
            nb_cpus = stats["cpu_stats"].get("online_cpus") or len(
                stats["cpu_stats"]["cpu_usage"].get("percpu_usage", [1])
            )
            if system_delta > 0:
                return (cpu_delta / system_delta) * nb_cpus * 100.0
        except (KeyError, ZeroDivisionError):
            pass
        return 0.0

    def _parse_stats(self, container, stats: dict) -> ServiceMetrics:
        service_name: str = container.labels.get(COMPOSE_LABEL_SERVICE, container.name)
        mem: dict = stats.get("memory_stats", {})
        mem_limit: int = max(mem.get("limit", 1), 1)

        net_rx = net_tx = 0.0
        for iface in stats.get("networks", {}).values():
            net_rx += iface.get("rx_bytes", 0)
            net_tx += iface.get("tx_bytes", 0)

        blk_read = blk_write = 0
        for blk in stats.get("blkio_stats", {}).get("io_service_bytes_recursive") or []:
            if blk.get("op") == _BLKIO_OP_READ:
                blk_read += blk.get("value", 0)
            elif blk.get("op") == _BLKIO_OP_WRITE:
                blk_write += blk.get("value", 0)

        return ServiceMetrics(
            service=service_name,
            container_id=container.short_id,
            status=container.status,
            cpu_percent=round(self._calc_cpu_percent(stats), 2),
            mem_usage_mb=self._bytes_to_mb(mem.get("usage", 0)),
            mem_limit_mb=self._bytes_to_mb(mem.get("limit", 1)),
            mem_percent=round((mem.get("usage", 0) / mem_limit) * 100, 2),
            net_rx_mb=self._bytes_to_mb(int(net_rx)),
            net_tx_mb=self._bytes_to_mb(int(net_tx)),
            block_read_mb=self._bytes_to_mb(blk_read),
            block_write_mb=self._bytes_to_mb(blk_write),
        )

    def _zero_metrics(self, container) -> ServiceMetrics:
        return ServiceMetrics(
            service=container.labels.get(COMPOSE_LABEL_SERVICE, container.name),
            container_id=container.short_id,
            status=container.status,
            cpu_percent=0, mem_usage_mb=0, mem_limit_mb=0, mem_percent=0,
            net_rx_mb=0, net_tx_mb=0, block_read_mb=0, block_write_mb=0,
        )

    def get_project_metrics(self, project_id: str) -> list[ServiceMetrics]:
        result: list[ServiceMetrics] = []
        for container in docker_client.get_all_containers_for_project(project_id):
            try:
                result.append(self._parse_stats(container, container.stats(stream=False)))
            except Exception:
                result.append(self._zero_metrics(container))
        return result


metrics_service = MetricsService()
