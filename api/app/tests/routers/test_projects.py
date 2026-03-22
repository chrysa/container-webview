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
            """Return 200 with all discovered projects.

            Given: project_manager.list_all returns 2 projects
            When: GET /api/projects with valid auth
            Then: Should return 200 with a JSON array of 2 items
            """
            mocker.patch(
                "app.routers.projects.project_manager.list_all",
                return_value=[_make_project("proj-a"), _make_project("proj-b")],
            )
            async with api_client() as client:
                response = await client.get("/api/projects", headers=auth_headers())

            assert response.status_code == 200, f"Expected 200 but got {response.status_code=}"
            body = response.json()
            assert len(body) == 2, f"Expected 2 projects but got {len(body)=}"
            ids = {p["id"] for p in body}
            assert ids == {"proj-a", "proj-b"}, f"Expected project ids but got {ids=}"

        async def test_returns_401_without_token(self, api_client):
            """Return 401 when no token is provided.

            Given: No Authorization header
            When: GET /api/projects
            Then: Should return 401
            """
            async with api_client() as client:
                response = await client.get("/api/projects")

            assert response.status_code == 401, f"Expected 401 but got {response.status_code=}"

    class TestGetProject:
        """Tests for GET /api/projects/{project_id}."""

        async def test_returns_project_when_found(self, api_client, auth_headers, mocker):
            """Return 200 with the project when it exists.

            Given: project_manager.load returns a valid ProjectModel
            When: GET /api/projects/my-project with valid auth
            Then: Should return 200 with the project data
            """
            mocker.patch(
                "app.routers.projects.project_manager.load",
                return_value=_make_project("my-project"),
            )
            async with api_client() as client:
                response = await client.get("/api/projects/my-project", headers=auth_headers())

            assert response.status_code == 200, f"Expected 200 but got {response.status_code=}"
            assert response.json()["id"] == "my-project", f"Unexpected id {response.json()['id']=}"

        async def test_returns_404_when_project_not_found(self, api_client, auth_headers, mocker):
            """Return 404 when the project does not exist.

            Given: project_manager.load returns None
            When: GET /api/projects/unknown with valid auth
            Then: Should return 404
            """
            mocker.patch(
                "app.routers.projects.project_manager.load",
                return_value=None,
            )
            async with api_client() as client:
                response = await client.get("/api/projects/unknown", headers=auth_headers())

            assert response.status_code == 404, f"Expected 404 but got {response.status_code=}"
