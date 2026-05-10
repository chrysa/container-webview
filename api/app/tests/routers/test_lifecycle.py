import pytest


class TestLifecycleActions:
    """Tests for the lifecycle action endpoints."""

    @pytest.mark.parametrize("action", ["start", "stop", "restart", "pause", "unpause"])
    async def test_returns_200_on_success(self, action, api_client, auth_headers, mocker):
        mock_service = mocker.MagicMock()
        mock_service.name = "web"
        mocker.patch(
            "app.routers.lifecycle.load_project",
            return_value=mocker.MagicMock(services=[mock_service]),
        )
        mock_container = mocker.MagicMock()
        mock_container.status = "running"
        mocker.patch("app.routers.lifecycle.get_container_for_service", return_value=mock_container)
        async with api_client() as client:
            response = await client.post(
                f"/api/projects/my-project/services/web/{action}",
                headers=auth_headers(),
            )
        assert response.status_code == 200
        body = response.json()
        assert body["service"] == "web"
        assert body["action"] == action

    async def test_returns_404_when_project_not_found(self, api_client, auth_headers, mocker):
        mocker.patch("app.routers.lifecycle.load_project", return_value=None)
        async with api_client() as client:
            response = await client.post(
                "/api/projects/missing/services/web/start",
                headers=auth_headers(),
            )
        assert response.status_code == 404

    async def test_returns_404_when_container_not_found(self, api_client, auth_headers, mocker):
        mock_service = mocker.MagicMock()
        mock_service.name = "unknown"
        mocker.patch(
            "app.routers.lifecycle.load_project",
            return_value=mocker.MagicMock(services=[mock_service]),
        )
        mocker.patch("app.routers.lifecycle.get_container_for_service", return_value=None)
        async with api_client() as client:
            response = await client.post(
                "/api/projects/proj/services/unknown/stop",
                headers=auth_headers(),
            )
        assert response.status_code == 404

    async def test_returns_401_without_token(self, api_client):
        async with api_client() as client:
            response = await client.post("/api/projects/proj/services/web/start")
        assert response.status_code == 401

