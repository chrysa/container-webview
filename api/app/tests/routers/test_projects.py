<<<<<<< HEAD
import pytest


@pytest.fixture(name="fixt_project")
def fixt_project():
    """Build a minimal ProjectModel dict for mocking."""
    from app.services.project_manager import ProjectModel
    from app.services.project_manager import ServiceModel

    def _load(**kwargs):
        return ProjectModel(
            id=kwargs.get("id", "my-project"),
            name=kwargs.get("name", "my-project"),
            path=kwargs.get("path", "/projects/my-project"),
            compose_file=kwargs.get("compose_file", "docker-compose.yml"),
            services=[
                ServiceModel(name="web", image="nginx:latest"),
                ServiceModel(name="db", image="postgres:15"),
            ],
        )

    return _load


class TestListProjects:
    """Tests for GET /api/projects."""

    async def test_returns_project_list(self, api_client, auth_headers, fixt_project, mocker):
        """Return list of projects when authenticated.

        Given: Two projects on the filesystem, user is authenticated
        When: GET /api/projects
        Then: Should return 200 with the list of ProjectModel
        """
        projects = [fixt_project(id="proj-a"), fixt_project(id="proj-b")]
        mocker.patch("app.routers.projects.list_projects", return_value=projects)

        async with api_client() as client:
            response = await client.get("/api/projects", headers=auth_headers())

        assert response.status_code == 200, f"Expected 200 but got {response.status_code=}"
        body = response.json()
        assert len(body) == 2, f"Expected 2 projects but got {len(body)=}"
        assert body[0]["id"] == "proj-a", f"Unexpected first project id: {body[0]['id']=}"

    async def test_returns_empty_list_when_no_projects(self, api_client, auth_headers, mocker):
        """Return empty list when no projects are configured.

        Given: No projects on the filesystem
        When: GET /api/projects
        Then: Should return 200 with empty list
        """
        mocker.patch("app.routers.projects.list_projects", return_value=[])

        async with api_client() as client:
            response = await client.get("/api/projects", headers=auth_headers())

        assert response.status_code == 200, f"Expected 200 but got {response.status_code=}"
        assert response.json() == [], f"Expected empty list but got {response.json()=}"

    async def test_requires_authentication(self, api_client):
        """Reject unauthenticated request.

        Given: No Authorization header
        When: GET /api/projects
        Then: Should return 401 Unauthorized
        """
        async with api_client() as client:
            response = await client.get("/api/projects")

        assert response.status_code == 401, f"Expected 401 but got {response.status_code=}"


class TestGetProject:
    """Tests for GET /api/projects/{project_id}."""

    async def test_returns_project_by_id(self, api_client, auth_headers, fixt_project, mocker):
        """Return a single project when it exists.

        Given: A project with id 'my-project' exists
        When: GET /api/projects/my-project
        Then: Should return 200 with the ProjectModel
        """
        project = fixt_project(id="my-project")
        mocker.patch("app.routers.projects.load_project", return_value=project)

        async with api_client() as client:
            response = await client.get("/api/projects/my-project", headers=auth_headers())

        assert response.status_code == 200, f"Expected 200 but got {response.status_code=}"
        body = response.json()
        assert body["id"] == "my-project", f"Unexpected id: {body['id']=}"
        assert len(body["services"]) == 2, f"Expected 2 services but got {len(body['services'])=}"

    async def test_returns_404_when_project_not_found(self, api_client, auth_headers, mocker):
        """Return 404 when project does not exist.

        Given: No project matching the given id
        When: GET /api/projects/unknown
        Then: Should return 404 Not Found
        """
        mocker.patch("app.routers.projects.load_project", return_value=None)

        async with api_client() as client:
            response = await client.get("/api/projects/unknown", headers=auth_headers())

        assert response.status_code == 404, f"Expected 404 but got {response.status_code=}"

    async def test_requires_authentication(self, api_client):
        """Reject unauthenticated request.

        Given: No Authorization header
        When: GET /api/projects/any
        Then: Should return 401 Unauthorized
        """
        async with api_client() as client:
            response = await client.get("/api/projects/any")

        assert response.status_code == 401, f"Expected 401 but got {response.status_code=}"
||||||| parent of 62afd77 (test(api): add unit tests, fix guidelines violations, update docs\n\n- Single outer test class with nested sub-classes (no multiple module-level classes)\n- No type annotations in test helpers or factory functions\n- No imports inside fixture/method bodies\n- No noqa comments\n- mocker.patch for all mocking, Given-When-Then docstrings\n- conftest: move security import to module level\n- docs: rewrite README, update changelog, fix stale make targets")
=======
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
>>>>>>> 62afd77 (test(api): add unit tests, fix guidelines violations, update docs\n\n- Single outer test class with nested sub-classes (no multiple module-level classes)\n- No type annotations in test helpers or factory functions\n- No imports inside fixture/method bodies\n- No noqa comments\n- mocker.patch for all mocking, Given-When-Then docstrings\n- conftest: move security import to module level\n- docs: rewrite README, update changelog, fix stale make targets")
