from pydantic import BaseModel

from app.constants import ContainerState
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
    """2-D coordinates for a graph node."""

    x: float
    y: float


class GraphNode(BaseModel):
    """A node in the topology graph."""

    id: str
    type: str  # "service" | "network"
    data: dict
    position: NodePosition


class GraphEdge(BaseModel):
    """A directed edge in the topology graph."""

    id: str
    source: str
    target: str
    label: str | None = None
    animated: bool = False


class TopologyGraph(BaseModel):
    """Full topology graph for a Compose project."""

    nodes: list[GraphNode]
    edges: list[GraphEdge]


class TopologyService:
    """Builds a topology graph from a Compose project definition."""

    @staticmethod
    def _network_color_map(networks: list[str]) -> dict[str, str]:
        """Assign a distinct display colour to each network."""
        return {network_name: _NETWORK_COLORS[i % len(_NETWORK_COLORS)] for i, network_name in enumerate(networks)}

    @staticmethod
    def _service_nodes_and_edges(
        project: ProjectModel,
        project_id: str,
        color_map: dict[str, str],
    ) -> tuple[list[GraphNode], list[GraphEdge]]:
        """Return service nodes and depends-on edges for a project."""
        nodes: list[GraphNode] = []
        edges: list[GraphEdge] = []

        for service_index, service in enumerate(project.services):
            column_index, row_index = service_index % _GRID_COLS, service_index // _GRID_COLS
            status: str = docker_client.get_container_status(project_id, service.name)
            bg_color: str = (
                color_map.get(service.networks[0], _DEFAULT_NODE_COLOR)
                if service.networks
                else _DEFAULT_NODE_COLOR
            )

            nodes.append(GraphNode(
                id=f"{_ID_PREFIX_SVC}{service.name}",
                type=_NODE_TYPE_SERVICE,
                position=NodePosition(x=100 + column_index * 280, y=100 + row_index * 200),
                data={
                    "label": service.name,
                    "image": service.image or "",
                    "status": status,
                    "ports": service.ports,
                    "networks": service.networks,
                    "bgColor": bg_color,
                },
            ))

            for dependency_name in service.depends_on:
                edges.append(GraphEdge(
                    id=f"{_ID_PREFIX_DEP}{dependency_name}-{service.name}",
                    source=f"{_ID_PREFIX_SVC}{dependency_name}",
                    target=f"{_ID_PREFIX_SVC}{service.name}",
                    label=_EDGE_LABEL_DEPENDS_ON,
                    animated=status == ContainerState.RUNNING,
                ))

        return nodes, edges

    @staticmethod
    def _network_nodes_and_edges(
        project: ProjectModel,
        color_map: dict[str, str],
    ) -> tuple[list[GraphNode], list[GraphEdge]]:
        """Return network nodes and service-to-network membership edges."""
        nodes: list[GraphNode] = []
        edges: list[GraphEdge] = []

        for i, network_name in enumerate(project.networks):
            nodes.append(GraphNode(
                id=f"{_ID_PREFIX_NET}{network_name}",
                type=_NODE_TYPE_NETWORK,
                position=NodePosition(x=50 + i * 200, y=600),
                data={"label": network_name, "color": color_map[network_name]},
            ))
            for service in project.services:
                if network_name in service.networks:
                    edges.append(GraphEdge(
                        id=f"{_ID_PREFIX_NET}{service.name}-{network_name}",
                        source=f"{_ID_PREFIX_SVC}{service.name}",
                        target=f"{_ID_PREFIX_NET}{network_name}",
                    ))

        return nodes, edges

    def build(self, project_id: str) -> TopologyGraph | None:
        """Build and return the topology graph, or None if the project does not exist."""
        project = project_manager.load(project_id)
        if not project:
            return None

        color_map = self._network_color_map(project.networks)
        svc_nodes, svc_edges = self._service_nodes_and_edges(project, project_id, color_map)
        net_nodes, net_edges = self._network_nodes_and_edges(project, color_map)

        return TopologyGraph(nodes=svc_nodes + net_nodes, edges=svc_edges + net_edges)


topology_service = TopologyService()
