import contextlib

import docker.errors
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from pydantic import BaseModel

from app.security import get_current_user
from app.services.docker_client import get_docker_client
from app.services.project_manager import load_project


router = APIRouter()

# Palette de couleurs par réseau
NETWORK_COLORS = [
    "#4f86f7",
    "#f76f4f",
    "#4ff79f",
    "#f7e94f",
    "#c74ff7",
    "#4ff7f0",
    "#f74fa8",
    "#a8f74f",
]


class NodePosition(BaseModel):
    x: float
    y: float


class GraphNode(BaseModel):
    id: str
    type: str  # "service" | "volume" | "network"
    data: dict
    position: NodePosition


class GraphEdge(BaseModel):
    id: str
    source: str
    target: str
    label: str | None = None
    animated: bool = False


class TopologyGraph(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]


def _get_container_status(project_id: str, service_name: str) -> str:
    with contextlib.suppress(docker.errors.DockerException):
        client = get_docker_client()
        for container in client.containers.list(all=True):
            labels = container.labels
            if (
                labels.get("com.docker.compose.project") == project_id
                and labels.get("com.docker.compose.service") == service_name
            ):
                return container.status
    return "unknown"


@router.get("/{project_id}/topology", response_model=TopologyGraph)
def get_topology(project_id: str, _: dict = Depends(get_current_user)) -> TopologyGraph:
    project = load_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projet introuvable")

    nodes: list[GraphNode] = []
    edges: list[GraphEdge] = []

    network_color_map: dict = {}
    for i, net in enumerate(project.networks):
        network_color_map[net] = NETWORK_COLORS[i % len(NETWORK_COLORS)]

    cols = 3
    for idx, svc in enumerate(project.services):
        col = idx % cols
        row = idx // cols
        x = 100 + col * 280
        y = 100 + row * 200

        status = _get_container_status(project_id, svc.name)

        bg_color = "#334155"
        if svc.networks:
            bg_color = network_color_map.get(svc.networks[0], "#334155")

        nodes.append(
            GraphNode(
                id=f"svc-{svc.name}",
                type="service",
                position=NodePosition(x=x, y=y),
                data={
                    "label": svc.name,
                    "image": svc.image or "",
                    "status": status,
                    "ports": svc.ports,
                    "networks": svc.networks,
                    "bgColor": bg_color,
                },
            )
        )

        edges.extend(
            GraphEdge(
                id=f"dep-{dep}-{svc.name}",
                source=f"svc-{dep}",
                target=f"svc-{svc.name}",
                label="depends_on",
                animated=status == "running",
            )
            for dep in svc.depends_on
        )

    for i, net in enumerate(project.networks):
        nodes.append(
            GraphNode(
                id=f"net-{net}",
                type="network",
                position=NodePosition(x=50 + i * 200, y=600),
                data={"label": net, "color": network_color_map[net]},
            )
        )
        edges.extend(
            GraphEdge(
                id=f"net-{svc.name}-{net}",
                source=f"svc-{svc.name}",
                target=f"net-{net}",
                animated=False,
            )
            for svc in project.services
            if net in svc.networks
        )

    return TopologyGraph(nodes=nodes, edges=edges)
