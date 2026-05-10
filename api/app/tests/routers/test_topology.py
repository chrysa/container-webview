from app.services.project_manager import ProjectModel
from app.services.project_manager import ServiceModel


def _make_project(project_id="my-project"):
    return ProjectModel(
        id=project_id,
        name="My Project",
        path=f"/projects/{project_id}",
        compose_file="docker-compose.yml",
        services=[
            ServiceModel(name="web", image="nginx", ports=[], depends_on=[], networks=[], volumes=[], environment={})
        ],
        networks=[],
    )


class TestGetTopology:
    """Tests for GET /api/projects/{project_id}/topology."""

    async def test_returns_topology_for_existing_project(self, api_client, auth_headers, mocker):
        mocker.patch("app.routers.topology.load_project", return_value=_make_project("my-project"))
        mocker.patch("app.routers.topology._get_container_status", return_value="running")
        async with api_client() as client:
            response = await client.get("/api/projects/my-project/topology", headers=auth_headers())
        assert response.status_code == 200
        body = response.json()
        assert "nodes" in body
        assert "edges" in body
        assert len(body["nodes"]) >= 1

    async def test_returns_404_when_project_not_found(self, api_client, auth_headers, mocker):
        mocker.patch("app.routers.topology.load_project", return_value=None)
        async with api_client() as client:
            response = await client.get("/api/projects/unknown/topology", headers=auth_headers())
        assert response.status_code == 404

    async def test_returns_401_without_token(self, api_client):
        async with api_client() as client:
            response = await client.get("/api/projects/my-project/topology")
        assert response.status_code == 401
