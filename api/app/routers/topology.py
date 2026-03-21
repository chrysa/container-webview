from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel

from app.security import get_current_user
from app.services.project_manager import load_project
from app.services.docker_client import get_docker_client

router = APIRouter()

# Palette de couleurs par réseau
NETWORK_COLORS = [
    "#4f86f7", "#f76f4f", "#4ff79f", "#f7e94f",
    "#c74ff7", "#4ff7f0", "#f74fa8", "#a8f74f",
]


class NodePosition(BaseModel):
    x: float
    y: float


class GraphNode(BaseModel):
    id: str
    type: str           # "service" | "volume" | "network"
    data: dict
    position: NodePosition


class GraphEdge(BaseModel):
    id: str
    source: str
    target: str
    label: Optional[str] = None
    animated: bool = False


class TopologyGraph(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]


def _get_container_status(project_id: str, service_name: str) -> str:
    try:
        client = get_docker_client()
        for container in client.containers.list(all=True):
            labels = container.labels
            if (labels.get("com.docker.compose.project") == project_id and
                    labels.get("com.docker.compose.service") == service_name):
                return container.status  # running, exited, paused, etc.
    except Exception:
        pass
    return "unknown"


@router.get("/{project_id}/topology", response_model=TopologyGraph)
def get_topology(project_id: str, _: dict = Depends(get_current_user)):
    project = load_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projet introuvable")

    nodes: List[GraphNode] = []
    edges: List[GraphEdge] = []

    # --- Couleur par réseau ---
    network_color_map: dict = {}
    for i, net in enumerate(project.networks):
        network_color_map[net] = NETWORK_COLORS[i % len(NETWORK_COLORS)]

    # Placement automatique en grille (peut être overridé par le front)
    cols = 3
    for idx, svc in enumerate(project.services):
        col = idx % cols
        row = idx // cols
        x = 100 + col * 280
        y = 100 + row * 200

        status = _get_container_status(project_id, svc.name)

        # Couleur de fond selon le réseau principal du service
        bg_color = "#334155"
        if svc.networks:
            bg_color = network_color_map.get(svc.networks[0], "#334155")

        nodes.append(GraphNode(
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
        ))

        # Edges depends_on
        for dep in svc.depends_on:
            edges.append(GraphEdge(
                id=f"dep-{dep}-{svc.name}",
                source=f"svc-{dep}",
                target=f"svc-{svc.name}",
                label="depends_on",
                animated=status == "running",
            ))

    # --- Nœuds réseau ---
    for i, net in enumerate(project.networks):
        nodes.append(GraphNode(
            id=f"net-{net}",
            type="network",
            position=NodePosition(x=50 + i * 200, y=600),
            data={"label": net, "color": network_color_map[net]},
        ))
        # Edges service → réseau
        for svc in project.services:
            if net in svc.networks:
                edges.append(GraphEdge(
                    id=f"net-{svc.name}-{net}",
                    source=f"svc-{svc.name}",
                    target=f"net-{net}",
                    animated=False,
                ))

    return TopologyGraph(nodes=nodes, edges=edges)
