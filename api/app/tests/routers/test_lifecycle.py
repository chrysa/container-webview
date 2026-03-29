import pytest

from app.constants import ContainerState
from app.constants import ERR_CONTAINER_NOT_FOUND
from app.constants import ERR_PROJECT_NOT_FOUND
from app.constants import ERR_SERVICE_NOT_FOUND


class TestLifecycleActions:
    """Tests for the lifecycle action endpoints."""

    @pytest.mark.parametrize("action", ["start", "stop", "restart", "pause", "unpause"])
    async def test_returns_200_on_success(self, action, api_client, auth_headers, mocker):
        """Return 200 with ActionResponse when the action succeeds.

        Given: lifecycle_service.perform returns the resulting container state
        When: POST /api/projects/{id}/services/{svc}/{action} with valid auth
        Then: Should return 200 with service, action and status fields
        """
        mocker.patch(
            "app.routers.lifecycle.lifecycle_service.perform",
            return_value=ContainerState.RUNNING,
        )
        async with api_client() as client:
            response = await client.post(
                f"/api/projects/my-project/services/web/{action}",
                headers=auth_headers(),
            )

        assert response.status_code == 200, f"Expected 200 but got {response.status_code=}"
        body = response.json()
        assert body["service"] == "web", f"Expected 'web' but got {body['service']=}"
        assert body["action"] == action, f"Expected {action!r} but got {body['action']=}"
        assert body["status"] == ContainerState.RUNNING, (
            f"Expected RUNNING but got {body['status']=}"
        )

    async def test_returns_404_when_project_not_found(self, api_client, auth_headers, mocker):
        """Return 404 when the project does not exist.

        Given: lifecycle_service.perform raises ValueError with ERR_PROJECT_NOT_FOUND
        When: POST /api/projects/missing/services/web/start
        Then: Should return 404
        """
        mocker.patch(
            "app.routers.lifecycle.lifecycle_service.perform",
            side_effect=ValueError(ERR_PROJECT_NOT_FOUND),
        )
        async with api_client() as client:
            response = await client.post(
                "/api/projects/missing/services/web/start",
                headers=auth_headers(),
            )

        assert response.status_code == 404, f"Expected 404 but got {response.status_code=}"

    async def test_returns_404_when_container_not_found(self, api_client, auth_headers, mocker):
        """Return 404 when the container does not exist.

        Given: lifecycle_service.perform raises ValueError with ERR_CONTAINER_NOT_FOUND
        When: POST /api/projects/proj/services/unknown/stop
        Then: Should return 404
        """
        mocker.patch(
            "app.routers.lifecycle.lifecycle_service.perform",
            side_effect=ValueError(ERR_CONTAINER_NOT_FOUND.format("unknown")),
        )
        async with api_client() as client:
            response = await client.post(
                "/api/projects/proj/services/unknown/stop",
                headers=auth_headers(),
            )

        assert response.status_code == 404, f"Expected 404 but got {response.status_code=}"

    async def test_returns_400_for_unknown_action_error(self, api_client, auth_headers, mocker):
        """Return 400 when ValueError is raised for an unrecognised reason.

        Given: lifecycle_service.perform raises ValueError with an unknown message
        When: Calling any lifecycle endpoint
        Then: Should return 400
        """
        mocker.patch(
            "app.routers.lifecycle.lifecycle_service.perform",
            side_effect=ValueError("Unknown action: fly"),
        )
        async with api_client() as client:
            response = await client.post(
                "/api/projects/proj/services/web/start",
                headers=auth_headers(),
            )

        assert response.status_code == 400, f"Expected 400 but got {response.status_code=}"

    async def test_returns_401_without_token(self, api_client):
        """Return 401 when no token is provided.

        Given: No Authorization header
        When: POST /api/projects/proj/services/web/start
        Then: Should return 401
        """
        async with api_client() as client:
            response = await client.post("/api/projects/proj/services/web/start")

        assert response.status_code == 401, f"Expected 401 but got {response.status_code=}"
