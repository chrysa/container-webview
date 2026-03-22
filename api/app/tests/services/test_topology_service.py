import pytest

from app.constants import ContainerState
from app.services.project_manager import ProjectModel, ServiceModel
from app.services.topology_service import (
    TopologyService,
    _ID_PREFIX_NET,
    _ID_PREFIX_SVC,
    _NETWORK_COLORS,
)


def _make_project(services=None, networks=None):
    """Build a minimal ProjectModel for topology tests."""
    return ProjectModel(
        id="test-project",
        name="Test Project",
        path="/tmp/test-project",
        compose_file="docker-compose.yml",
        services=services or [],
        networks=networks or [],
    )


def _make_service(name, image="nginx:alpine", networks=None, depends_on=None):
    return ServiceModel(
        name=name,
        image=image,
        ports=[],
        depends_on=depends_on or [],
        networks=networks or [],
    )


class TestTopologyService:
    """Unit tests for TopologyService."""

    class TestNetworkColorMap:
        """Tests for _network_color_map() static method."""

        def test_assigns_color_to_each_network(self):
            """Return a color for every network in the input list.

            Given: Three network names
            When: Calling _network_color_map(['frontend', 'backend', 'db'])
            Then: Should return a dict mapping each name to a hex color string
            """
            result = TopologyService._network_color_map(["frontend", "backend", "db"])
            assert len(result) == 3, f"Expected 3 entries but got {len(result)=}"
            for name in ["frontend", "backend", "db"]:
                assert name in result, f"Expected {name} in color map but got {result=}"
                assert result[name].startswith("#"), f"Expected hex color but got {result[name]=}"

        def test_wraps_colors_when_more_networks_than_palette(self):
            """Cycle through the color palette when there are more networks than colors.

            Given: 9 networks (more than the 8-color palette)
            When: Calling _network_color_map(...)
            Then: The 9th network should reuse the first color of the palette
            """
            networks = [f"net-{i}" for i in range(len(_NETWORK_COLORS) + 1)]
            result = TopologyService._network_color_map(networks)
            assert result["net-0"] == result[f"net-{len(_NETWORK_COLORS)}"], (
                f"Expected color wrap-around but got {result['net-0']=} vs {result[f'net-{len(_NETWORK_COLORS)}']!r}"
            )

        def test_returns_empty_dict_for_empty_list(self):
            """Return empty dict for an empty network list.

            Given: An empty list
            When: Calling _network_color_map([])
            Then: Should return {}
            """
            result = TopologyService._network_color_map([])
            assert result == {}, f"Expected {{}} but got {result=}"

    class TestBuild:
        """Tests for build()."""

        def test_returns_none_when_project_not_found(self, mocker):
            """Return None when project_manager.load returns None.

            Given: A project_id that does not resolve to any project
            When: Calling build('no-such-project')
            Then: Should return None
            """
            mocker.patch(
                "app.services.topology_service.project_manager.load",
                return_value=None,
            )
            service = TopologyService()
            result = service.build("no-such-project")
            assert result is None, f"Expected None but got {result=}"

        def test_returns_topology_graph_for_valid_project(self, mocker):
            """Return a TopologyGraph with service and network nodes.

            Given: A project with 2 services connected to 1 network
            When: Calling build('test-project')
            Then: Should return TopologyGraph with 3 nodes (2 svc + 1 net) and 2 edges
            """
            project = _make_project(
                services=[
                    _make_service("api", networks=["app-net"]),
                    _make_service("db", networks=["app-net"]),
                ],
                networks=["app-net"],
            )
            mocker.patch(
                "app.services.topology_service.project_manager.load",
                return_value=project,
            )
            mocker.patch(
                "app.services.topology_service.docker_client.get_container_status",
                return_value=ContainerState.RUNNING,
            )

            service = TopologyService()
            result = service.build("test-project")

            assert result is not None, "Expected TopologyGraph but got None"
            node_ids = {n.id for n in result.nodes}
            assert f"{_ID_PREFIX_SVC}api" in node_ids, f"Expected svc-api in {node_ids=}"
            assert f"{_ID_PREFIX_SVC}db" in node_ids, f"Expected svc-db in {node_ids=}"
            assert f"{_ID_PREFIX_NET}app-net" in node_ids, f"Expected net-app-net in {node_ids=}"

        def test_service_edges_are_animated_when_running(self, mocker):
            """Edges for depends_on are animated when the dependent service is RUNNING.

            Given: Service 'api' depends_on 'db' and the container is RUNNING
            When: Calling build(...)
            Then: The depends_on edge should have animated=True
            """
            project = _make_project(
                services=[
                    _make_service("db"),
                    _make_service("api", depends_on=["db"]),
                ],
                networks=[],
            )
            mocker.patch(
                "app.services.topology_service.project_manager.load",
                return_value=project,
            )
            mocker.patch(
                "app.services.topology_service.docker_client.get_container_status",
                return_value=ContainerState.RUNNING,
            )

            service = TopologyService()
            result = service.build("test-project")

            dep_edges = [e for e in result.edges if "db" in e.id and "api" in e.id]
            assert len(dep_edges) == 1, f"Expected 1 depends_on edge but got {dep_edges=}"
            assert dep_edges[0].animated is True, (
                f"Expected animated=True for running service but got {dep_edges[0].animated=}"
            )

        def test_service_edges_are_not_animated_when_stopped(self, mocker):
            """Edges for depends_on are not animated when the dependent service is stopped.

            Given: Service 'api' depends_on 'db' and the container is EXITED
            When: Calling build(...)
            Then: The depends_on edge should have animated=False
            """
            project = _make_project(
                services=[
                    _make_service("db"),
                    _make_service("api", depends_on=["db"]),
                ],
                networks=[],
            )
            mocker.patch(
                "app.services.topology_service.project_manager.load",
                return_value=project,
            )
            mocker.patch(
                "app.services.topology_service.docker_client.get_container_status",
                return_value=ContainerState.EXITED,
            )

            service = TopologyService()
            result = service.build("test-project")

            dep_edges = [e for e in result.edges if "db" in e.id and "api" in e.id]
            assert len(dep_edges) == 1, f"Expected 1 depends_on edge but got {dep_edges=}"
            assert dep_edges[0].animated is False, (
                f"Expected animated=False for stopped service but got {dep_edges[0].animated=}"
            )

    class TestServiceNodesAndEdges:
        """Tests for _service_nodes_and_edges() static method."""

        def test_creates_one_node_per_service(self, mocker):
            """Return N service nodes for N services.

            Given: A project with 3 services
            When: Calling _service_nodes_and_edges(project, 'test-project', {})
            Then: Should return 3 nodes
            """
            project = _make_project(
                services=[
                    _make_service("svc-a"),
                    _make_service("svc-b"),
                    _make_service("svc-c"),
                ],
            )
            mocker.patch(
                "app.services.topology_service.docker_client.get_container_status",
                return_value=ContainerState.UNKNOWN,
            )
            nodes, edges = TopologyService._service_nodes_and_edges(project, "test-project", {})
            assert len(nodes) == 3, f"Expected 3 nodes but got {len(nodes)=}"
            assert edges == [], f"Expected no edges but got {edges=}"

    class TestNetworkNodesAndEdges:
        """Tests for _network_nodes_and_edges() static method."""

        def test_creates_membership_edges(self):
            """Return one edge per service-to-network membership.

            Given: 2 services each on 'app-net' + 1 service not on the network
            When: Calling _network_nodes_and_edges(project, color_map)
            Then: Should return 1 network node and 2 membership edges
            """
            project = _make_project(
                services=[
                    _make_service("api", networks=["app-net"]),
                    _make_service("db", networks=["app-net"]),
                    _make_service("cache", networks=[]),
                ],
                networks=["app-net"],
            )
            color_map = {"app-net": "#4f86f7"}
            nodes, edges = TopologyService._network_nodes_and_edges(project, color_map)
            assert len(nodes) == 1, f"Expected 1 network node but got {len(nodes)=}"
            assert len(edges) == 2, f"Expected 2 membership edges but got {len(edges)=}"
