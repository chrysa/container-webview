from app.services.metrics_service import ServiceMetrics


def _make_metrics(service_name="web"):
    return ServiceMetrics(
        service=service_name,
        container_id="abc123",
        status="running",
        cpu_percent=12.5,
        mem_usage_mb=64.0,
        mem_limit_mb=512.0,
        mem_percent=12.5,
        net_rx_mb=1.0,
        net_tx_mb=0.5,
        block_read_mb=0.0,
        block_write_mb=0.0,
    )


class TestGetMetrics:
    """Tests for GET /api/projects/{project_id}/metrics."""

    async def test_returns_metrics_for_existing_project(self, api_client, auth_headers, mocker):
        """Return 200 with a list of ServiceMetrics for all services.

        Given: The project exists and metrics_service returns 2 metrics
        When: GET /api/projects/my-project/metrics with valid auth
        Then: Should return 200 with 2 items
        """
        mocker.patch("app.routers.metrics.project_manager.load", return_value=mocker.MagicMock())
        mocker.patch(
            "app.routers.metrics.metrics_service.get_project_metrics",
            return_value=[_make_metrics("api"), _make_metrics("db")],
        )
        async with api_client() as client:
            response = await client.get("/api/projects/my-project/metrics", headers=auth_headers())

        assert response.status_code == 200, f"Expected 200 but got {response.status_code=}"
        body = response.json()
        assert len(body) == 2, f"Expected 2 metrics but got {len(body)=}"
        services = {m["service"] for m in body}
        assert services == {"api", "db"}, f"Expected service names but got {services=}"

    async def test_returns_404_when_project_not_found(self, api_client, auth_headers, mocker):
        """Return 404 when the project does not exist.

        Given: project_manager.load returns None
        When: GET /api/projects/unknown/metrics with valid auth
        Then: Should return 404
        """
        mocker.patch("app.routers.metrics.project_manager.load", return_value=None)
        async with api_client() as client:
            response = await client.get("/api/projects/unknown/metrics", headers=auth_headers())

        assert response.status_code == 404, f"Expected 404 but got {response.status_code=}"

    async def test_returns_401_without_token(self, api_client):
        """Return 401 when no token is provided.

        Given: No Authorization header
        When: GET /api/projects/my-project/metrics
        Then: Should return 401
        """
        async with api_client() as client:
            response = await client.get("/api/projects/my-project/metrics")

        assert response.status_code == 401, f"Expected 401 but got {response.status_code=}"
