from datetime import UTC
from datetime import datetime

from app.routers.alerts import Alert


def _make_alert(project="my-project", service="web"):
    return Alert(
        id=f"{project}-{service}-exited",
        level="warning",
        project=project,
        service=service,
        message="Container is restarting",
        timestamp=datetime.now(UTC).isoformat(),
    )


class TestAlertsRouter:
    """Unit tests for the /api/alerts router."""

    class TestGetAlerts:
        """Tests for GET /api/alerts."""

        async def test_returns_all_alerts(self, api_client, auth_headers, mocker):
            mocker.patch(
                "app.routers.alerts._container_alerts",
                return_value=[_make_alert("proj-a"), _make_alert("proj-b")],
            )
            async with api_client() as client:
                response = await client.get("/api/alerts", headers=auth_headers())
            assert response.status_code == 200
            assert len(response.json()) == 2

        async def test_returns_empty_list_when_no_alerts(self, api_client, auth_headers, mocker):
            mocker.patch("app.routers.alerts._container_alerts", return_value=[])
            async with api_client() as client:
                response = await client.get("/api/alerts", headers=auth_headers())
            assert response.status_code == 200
            assert response.json() == []

        async def test_returns_401_without_token(self, api_client):
            async with api_client() as client:
                response = await client.get("/api/alerts")
            assert response.status_code == 401
