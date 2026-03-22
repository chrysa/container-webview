from app.services.topology_service import GraphEdge, GraphNode, NodePosition, TopologyGraph


def _make_graph():
    return TopologyGraph(
        nodes=[
            GraphNode(
                id="svc-web",
                type="service",
                position=NodePosition(x=100, y=100),
                data={"label": "web", "image": "nginx", "status": "running", "ports": [], "networks": [], "bgColor": "#334155"},
            ),
        ],
        edges=[],
    )


class TestGetTopology:
    """Tests for GET /api/projects/{project_id}/topology."""

    async def test_returns_topology_for_existing_project(self, api_client, auth_headers, mocker):
        """Return 200 with a TopologyGraph when the project exists.

        Given: topology_service.build returns a valid TopologyGraph
        When: GET /api/projects/my-project/topology with valid auth
        Then: Should return 200 with nodes and edges fields
        """
        mocker.patch(
            "app.routers.topology.topology_service.build",
            return_value=_make_graph(),
        )
        async with api_client() as client:
            response = await client.get("/api/projects/my-project/topology", headers=auth_headers())

        assert response.status_code == 200, f"Expected 200 but got {response.status_code=}"
        body = response.json()
        assert "nodes" in body, f"Expected 'nodes' in {body=}"
        assert "edges" in body, f"Expected 'edges' in {body=}"
        assert len(body["nodes"]) == 1, f"Expected 1 node but got {len(body['nodes'])=}"

    async def test_returns_404_when_project_not_found(self, api_client, auth_headers, mocker):
        """Return 404 when the project does not exist.

        Given: topology_service.build returns None
        When: GET /api/projects/unknown/topology with valid auth
        Then: Should return 404
        """
        mocker.patch(
            "app.routers.topology.topology_service.build",
            return_value=None,
        )
        async with api_client() as client:
            response = await client.get("/api/projects/unknown/topology", headers=auth_headers())

        assert response.status_code == 404, f"Expected 404 but got {response.status_code=}"

    async def test_returns_401_without_token(self, api_client):
        """Return 401 when no token is provided."""
        async with api_client() as client:
            response = await client.get("/api/projects/my-project/topology")

        assert response.status_code == 401, f"Expected 401 but got {response.status_code=}"
