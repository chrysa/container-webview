"""Demo mode — every read path serves fixtures, no Docker socket access.

When ``settings.demo_mode`` is on, the projects/metrics/alerts/topology routers
must return fixture data and the auth router must accept the built-in demo
credentials, all without touching Docker or the filesystem.
"""

import pytest

from app import demo
from app.config import settings


@pytest.fixture(name="demo_on")
def fixt_demo_on(monkeypatch):
    """Enable demo mode for the duration of a test."""
    monkeypatch.setattr(settings, "demo_mode", True)


class TestConfigStatus:
    """Tests for GET /api/config/status."""

    async def test_reports_demo_mode_on(self, api_client, demo_on):
        async with api_client() as client:
            response = await client.get("/api/config/status")
        assert response.status_code == 200
        assert response.json()["demo_mode"] is True

    async def test_reports_demo_mode_off_by_default(self, api_client):
        async with api_client() as client:
            response = await client.get("/api/config/status")
        assert response.status_code == 200
        assert response.json()["demo_mode"] is False

    async def test_is_public(self, api_client, demo_on):
        async with api_client() as client:
            response = await client.get("/api/config/status")
        # No Authorization header — endpoint must still succeed.
        assert response.status_code == 200


class TestPingExposesDemoMode:
    """The public ping endpoint surfaces the demo flag."""

    async def test_ping_includes_demo_mode(self, api_client, demo_on):
        async with api_client() as client:
            response = await client.get("/api")
        assert response.status_code == 200
        assert response.json()["demo_mode"] is True


class TestDemoLogin:
    """Tests for demo credentials on POST /api/auth/login."""

    async def test_demo_credentials_accepted_when_demo_on(self, api_client, demo_on):
        async with api_client() as client:
            response = await client.post(
                "/api/auth/login",
                data={"username": demo.DEMO_USERNAME, "password": demo.DEMO_PASSWORD},
            )
        assert response.status_code == 200
        assert response.json()["access_token"]

    async def test_demo_credentials_rejected_when_demo_off(self, api_client):
        async with api_client() as client:
            response = await client.post(
                "/api/auth/login",
                data={"username": demo.DEMO_USERNAME, "password": demo.DEMO_PASSWORD},
            )
        assert response.status_code == 401


class TestDemoReadPaths:
    """Read endpoints return fixtures and never call Docker in demo mode."""

    async def test_projects_returns_fixtures(self, api_client, auth_headers, demo_on, mocker):
        spy = mocker.patch("app.routers.projects.list_projects")
        async with api_client() as client:
            response = await client.get("/api/projects", headers=auth_headers())
        assert response.status_code == 200
        body = response.json()
        assert len(body) == len(demo.list_projects())
        assert any(p["id"] == "demo-shop" for p in body)
        spy.assert_not_called()

    async def test_project_detail_returns_fixture(self, api_client, auth_headers, demo_on):
        async with api_client() as client:
            response = await client.get("/api/projects/demo-shop", headers=auth_headers())
        assert response.status_code == 200
        assert response.json()["id"] == "demo-shop"

    async def test_unknown_project_returns_404(self, api_client, auth_headers, demo_on):
        async with api_client() as client:
            response = await client.get("/api/projects/nope", headers=auth_headers())
        assert response.status_code == 404

    async def test_metrics_returns_fixtures(self, api_client, auth_headers, demo_on, mocker):
        spy = mocker.patch("app.routers.metrics.get_all_containers_for_project")
        async with api_client() as client:
            response = await client.get("/api/projects/demo-shop/metrics", headers=auth_headers())
        assert response.status_code == 200
        body = response.json()
        assert len(body) == 4
        assert all("cpu_percent" in m for m in body)
        spy.assert_not_called()

    async def test_alerts_returns_fixtures(self, api_client, auth_headers, demo_on, mocker):
        spy = mocker.patch("app.routers.alerts.get_docker_client")
        async with api_client() as client:
            response = await client.get("/api/alerts", headers=auth_headers())
        assert response.status_code == 200
        assert len(response.json()) == 2
        spy.assert_not_called()

    async def test_topology_returns_fixtures(self, api_client, auth_headers, demo_on, mocker):
        spy = mocker.patch("app.routers.topology.get_docker_client")
        async with api_client() as client:
            response = await client.get("/api/projects/demo-shop/topology", headers=auth_headers())
        assert response.status_code == 200
        body = response.json()
        assert body["nodes"]
        spy.assert_not_called()


class TestDemoLifecycle:
    """Lifecycle actions are no-ops that never touch Docker in demo mode."""

    async def test_start_returns_running_without_docker(self, api_client, auth_headers, demo_on, mocker):
        spy = mocker.patch("app.routers.lifecycle.get_container_for_service")
        async with api_client() as client:
            response = await client.post("/api/projects/demo-shop/services/web/start", headers=auth_headers())
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "running"
        assert "Demo mode" in body["message"]
        spy.assert_not_called()

    async def test_stop_returns_exited(self, api_client, auth_headers, demo_on):
        async with api_client() as client:
            response = await client.post("/api/projects/demo-shop/services/web/stop", headers=auth_headers())
        assert response.status_code == 200
        assert response.json()["status"] == "exited"

    async def test_unknown_service_returns_404(self, api_client, auth_headers, demo_on):
        async with api_client() as client:
            response = await client.post("/api/projects/demo-shop/services/ghost/start", headers=auth_headers())
        assert response.status_code == 404
