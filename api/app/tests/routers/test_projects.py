from app.services.project_manager import ProjectModel


def _make_project(project_id="my-project"):
    return ProjectModel(
        id=project_id,
        name="My Project",
        path=f"/projects/{project_id}",
        compose_file="docker-compose.yml",
        services=[],
        networks=[],
    )


class TestProjectsRouter:
    """Unit tests for the /api/projects router."""

    class TestGetProjects:
        """Tests for GET /api/projects."""

        async def test_returns_list_of_projects(self, api_client, auth_headers, mocker):
            mocker.patch(
                "app.routers.projects.list_projects",
                return_value=[_make_project("proj-a"), _make_project("proj-b")],
            )
            async with api_client() as client:
                response = await client.get("/api/projects", headers=auth_headers())
            assert response.status_code == 200
            body = response.json()
            assert len(body) == 2
            ids = {p["id"] for p in body}
            assert ids == {"proj-a", "proj-b"}

        async def test_returns_401_without_token(self, api_client):
            async with api_client() as client:
                response = await client.get("/api/projects")
            assert response.status_code == 401

    class TestGetProject:
        """Tests for GET /api/projects/{project_id}."""

        async def test_returns_project_when_found(self, api_client, auth_headers, mocker):
            mocker.patch(
                "app.routers.projects.load_project",
                return_value=_make_project("my-project"),
            )
            async with api_client() as client:
                response = await client.get("/api/projects/my-project", headers=auth_headers())
            assert response.status_code == 200
            assert response.json()["id"] == "my-project"

        async def test_returns_404_when_project_not_found(self, api_client, auth_headers, mocker):
            mocker.patch("app.routers.projects.load_project", return_value=None)
            async with api_client() as client:
                response = await client.get("/api/projects/unknown", headers=auth_headers())
            assert response.status_code == 404

        async def test_returns_401_without_token(self, api_client):
            async with api_client() as client:
                response = await client.get("/api/projects/my-project")
            assert response.status_code == 401
