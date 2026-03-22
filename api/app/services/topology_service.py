from typing import Optional

from pydantic import BaseModel

from app.constants import CONTAINER_RUNNING
from app.services.docker_client import docker_client
from app.services.project_manager import ProjectModel, project_manager

_NETWORK_COLORS: list[str] = [
    "#4f86f7", "#f76f4f", "#4ff79f", "#f7e94f",
    "#c74ff7", "#4ff7f0", "#f74fa8", "#a8f74f",
]
_DEFAULT_NODE_COLOR: str = "#334155"
_GRID_COLS: int = 3
_NODE_TYPE_SERVICE: str = "service"
_NODE_TYPE_NETWORK: str = "network"
_EDGE_LABEL_DEPENDS_ON: str = "depends_on"
_ID_PREFIX_SVC: str = "svc-"
_ID_PREFIX_NET: str = "net-"
_ID_PREFIX_DEP: str = "dep-"


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
    label: Optional[str] = None
    animated: bool = False


class TopologyGraph(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]


class TopologyService:
    @staticmethod
    def _network_color_map(networks: list[str]) -> dict[str, str]:
        return {net: _NETWORK_COLORS[i % len(_NETWORK_COLORS)] for i, net in enumerate(networks)}

    @staticmethod
    def _service_nodes_and_edges(
        project: ProjectModel,
        project_id: str,
        color_map: dict[str, str],
    ) -> tuple[list[GraphNode], list[GraphEdge]]:
        nodes: list[GraphNode] = []
        edges: list[GraphEdge] = []

        for idx, svc in enumerate(project.services):
            col, row = idx % _GRID_COLS, idx // _GRID_COLS
            status: str = docker_client.get_container_status(project_id, svc.name)
            bg_color: str = (
                color_map.get(svc.networks[0], _DEFAULT_NODE_COLOR)
                if svc.networks
                else _DEFAULT_NODE_COLOR
            )

            nodes.append(GraphNode(
                id=f"{_ID_PREFIX_SVC}{svc.name}",
                type=_NODE_TYPE_SERVICE,
                position=NodePosition(x=100 + col * 280, y=100 + row * 200),
                data={
                    "label": svc.name,
                    "image": svc.image or "",
                    "status": status,
                    "ports": svc.ports,
                    "networks": svc.networks,
                    "bgColor": bg_color,
                },
            ))

            for dep in svc.depends_on:
                edges.append(GraphEdge(
                    id=f"{_ID_PREFIX_DEP}{dep}-{svc.name}",
                    source=f"{_ID_PREFIX_SVC}{dep}",
                    target=f"{_ID_PREFIX_SVC}{svc.name}",
                    label=_EDGE_LABEL_DEPENDS_ON,
                    animated=status == CONTAINER_RUNNING,
                ))

        return nodes, edges

    @staticmethod
    def _network_nodes_and_edges(
        project: ProjectModel,
        color_map: dict[str, str],
    ) -> tuple[list[GraphNode], list[GraphEdge]]:
        nodes: list[GraphNode] = []
        edges: list[GraphEdge] = []

        for i, net in enumerate(project.networks):
            nodes.append(GraphNode(
                id=f"{_ID_PREFIX_NET}{net}",
                type=_NODE_TYPE_NETWORK,
                position=NodePosition(x=50 + i * 200, y=600),
                data={"label": net, "color": color_map[net]},
            ))
            for svc in project.services:
                if net in svc.networks:
                    edges.append(GraphEdge(
                        id=f"{_ID_PREFIX_NET}{svc.name}-{net}",
                        source=f"{_ID_PREFIX_SVC}{svc.name}",
                        target=f"{_ID_PREFIX_NET}{net}",
                    ))

        return nodes, edges

    def build(self, project_id: str) -> Optional[TopologyGraph]:
        project = project_manager.load(project_id)
        if not project:
            return None

        color_map = self._network_color_map(project.networks)
        svc_nodes, svc_edges = self._service_nodes_and_edges(project, project_id, color_map)
        net_nodes, net_edges = self._network_nodes_and_edges(project, color_map)

        return TopologyGraph(nodes=svc_nodes + net_nodes, edges=svc_edges + net_edges)


topology_service = TopologyService()
