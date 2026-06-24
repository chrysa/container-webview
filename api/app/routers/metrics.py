from docker.errors import APIError
from docker.models.containers import Container
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from pydantic import BaseModel

from app import demo
from app.config import settings
from app.security import get_current_user
from app.services.docker_client import get_all_containers_for_project
from app.services.project_manager import load_project


router = APIRouter()


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


def _calc_cpu_percent(stats: dict) -> float:
    try:
        cpu_delta = stats["cpu_stats"]["cpu_usage"]["total_usage"] - stats["precpu_stats"]["cpu_usage"]["total_usage"]
        system_delta = stats["cpu_stats"]["system_cpu_usage"] - stats["precpu_stats"]["system_cpu_usage"]
        nb_cpus = stats["cpu_stats"].get("online_cpus") or len(stats["cpu_stats"]["cpu_usage"].get("percpu_usage", [1]))
        if system_delta > 0:
            return (cpu_delta / system_delta) * nb_cpus * 100.0
    except (KeyError, ZeroDivisionError):
        pass
    return 0.0


def _bytes_to_mb(b: int) -> float:
    return round(b / (1024 * 1024), 2)


def _sum_network_bytes(stats: dict) -> tuple[float, float]:
    net_rx = net_tx = 0.0
    for iface_stats in stats.get("networks", {}).values():
        net_rx += iface_stats.get("rx_bytes", 0)
        net_tx += iface_stats.get("tx_bytes", 0)
    return net_rx, net_tx


def _sum_block_io_bytes(stats: dict) -> tuple[int, int]:
    blk_read = blk_write = 0
    for blk in stats.get("blkio_stats", {}).get("io_service_bytes_recursive") or []:
        if blk.get("op") == "Read":
            blk_read += blk.get("value", 0)
        elif blk.get("op") == "Write":
            blk_write += blk.get("value", 0)
    return blk_read, blk_write


def _build_service_metrics(service_name: str, container: Container, stats: dict) -> ServiceMetrics:
    mem = stats.get("memory_stats", {})
    mem_usage = _bytes_to_mb(mem.get("usage", 0))
    mem_limit = _bytes_to_mb(mem.get("limit", 1))
    mem_pct = round((mem.get("usage", 0) / max(mem.get("limit", 1), 1)) * 100, 2)

    net_rx, net_tx = _sum_network_bytes(stats)
    blk_read, blk_write = _sum_block_io_bytes(stats)

    return ServiceMetrics(
        service=service_name,
        container_id=container.short_id,
        status=container.status,
        cpu_percent=round(_calc_cpu_percent(stats), 2),
        mem_usage_mb=mem_usage,
        mem_limit_mb=mem_limit,
        mem_percent=mem_pct,
        net_rx_mb=_bytes_to_mb(int(net_rx)),
        net_tx_mb=_bytes_to_mb(int(net_tx)),
        block_read_mb=_bytes_to_mb(blk_read),
        block_write_mb=_bytes_to_mb(blk_write),
    )


def _empty_service_metrics(service_name: str, container: Container) -> ServiceMetrics:
    return ServiceMetrics(
        service=service_name,
        container_id=container.short_id,
        status=container.status,
        cpu_percent=0,
        mem_usage_mb=0,
        mem_limit_mb=0,
        mem_percent=0,
        net_rx_mb=0,
        net_tx_mb=0,
        block_read_mb=0,
        block_write_mb=0,
    )


_METRICS_RESPONSES: dict[int | str, dict] = {404: {"description": "Project not found"}}


@router.get("/{project_id}/metrics", response_model=list[ServiceMetrics], responses=_METRICS_RESPONSES)
def get_metrics(project_id: str, _: dict = Depends(get_current_user)) -> list[ServiceMetrics]:
    if settings.demo_mode:
        if not demo.load_project(project_id):
            raise HTTPException(status_code=404, detail="Projet introuvable")
        return [ServiceMetrics(**metrics) for metrics in demo.project_metrics(project_id)]

    project = load_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projet introuvable")

    containers = get_all_containers_for_project(project_id)
    result = []

    for container in containers:
        service_name = container.labels.get("com.docker.compose.service", container.name)
        try:
            stats = container.stats(stream=False)
            result.append(_build_service_metrics(service_name, container, stats))
        except APIError:
            result.append(_empty_service_metrics(service_name, container))

    return result
