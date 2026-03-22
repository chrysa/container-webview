from app.services.alerts_service import Alert
from app.services.alerts_service import AlertLevel


def _make_alert(project="my-project", service="web"):
    return Alert(
        id=f"{project}-{service}-test",
        project=project,
        service=service,
        level=AlertLevel.WARNING,
        message="Container is restarting",
        timestamp="2026-01-01T00:00:00+00:00",
    )


class TestAlertsRouter:
    """Unit tests for the /api/alerts router."""

    class TestGetAlerts:
        """Tests for GET /api/alerts."""

        async def test_returns_all_alerts(self, api_client, auth_headers, mocker):
            """Return 200 with all alerts across all containers.

            Given: alerts_service.get_all returns 2 alerts
            When: GET /api/alerts with valid auth
            Then: Should return 200 with 2 items
            """
            mocker.patch(
                "app.routers.alerts.alerts_service.get_all",
                return_value=[_make_alert("proj-a"), _make_alert("proj-b")],
            )
            async with api_client() as client:
                response = await client.get("/api/alerts", headers=auth_headers())

            assert response.status_code == 200, f"Expected 200 but got {response.status_code=}"
            assert len(response.json()) == 2, f"Expected 2 alerts but got {len(response.json())=}"

        async def test_returns_empty_list_when_no_alerts(self, api_client, auth_headers, mocker):
            """Return 200 with empty list when there are no alerts.

            Given: alerts_service.get_all returns []
            When: GET /api/alerts with valid auth
            Then: Should return 200 with []
            """
            mocker.patch("app.routers.alerts.alerts_service.get_all", return_value=[])
            async with api_client() as client:
                response = await client.get("/api/alerts", headers=auth_headers())

            assert response.status_code == 200, f"Expected 200 but got {response.status_code=}"
            assert response.json() == [], f"Expected [] but got {response.json()=}"

        async def test_returns_401_without_token(self, api_client):
            """Return 401 when no token is provided.

            Given: No Authorization header
            When: GET /api/alerts
            Then: Should return 401
            """
            async with api_client() as client:
                response = await client.get("/api/alerts")

            assert response.status_code == 401, f"Expected 401 but got {response.status_code=}"

    class TestGetProjectAlerts:
        """Tests for GET /api/alerts/project/{project_id}."""

        async def test_returns_alerts_for_project(self, api_client, auth_headers, mocker):
            """Return 200 with alerts filtered to the given project.

            Given: alerts_service.get_for_project returns 1 alert for 'my-project'
            When: GET /api/alerts/project/my-project with valid auth
            Then: Should return 200 with 1 item whose project field matches
            """
            mocker.patch(
                "app.routers.alerts.alerts_service.get_for_project",
                return_value=[_make_alert("my-project")],
            )
            async with api_client() as client:
                response = await client.get("/api/alerts/project/my-project", headers=auth_headers())

            assert response.status_code == 200, f"Expected 200 but got {response.status_code=}"
            body = response.json()
            assert len(body) == 1, f"Expected 1 alert but got {len(body)=}"
            assert body[0]["project"] == "my-project", f"Expected 'my-project' but got {body[0]['project']=}"
