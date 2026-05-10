class TestGetMetrics:
    """Tests for GET /api/projects/{project_id}/metrics."""

    async def test_returns_metrics_for_existing_project(self, api_client, auth_headers, mocker):
        mocker.patch("app.routers.metrics.load_project", return_value=mocker.MagicMock())
        mock_c1 = mocker.MagicMock()
        mock_c1.labels = {"com.docker.compose.service": "api"}
        mock_c1.name = "api"
        mock_c1.short_id = "abc123"
        mock_c1.status = "running"
        mock_c1.stats.return_value = {
            "cpu_stats": {"cpu_usage": {"total_usage": 1000}, "system_cpu_usage": 10000, "online_cpus": 1},
            "precpu_stats": {"cpu_usage": {"total_usage": 900}, "system_cpu_usage": 9000},
            "memory_stats": {"usage": 64 * 1024 * 1024, "limit": 512 * 1024 * 1024},
            "networks": {},
            "blkio_stats": {"io_service_bytes_recursive": []},
        }
        mocker.patch(
            "app.routers.metrics.get_all_containers_for_project",
            return_value=[mock_c1],
        )
        async with api_client() as client:
            response = await client.get("/api/projects/my-project/metrics", headers=auth_headers())
        assert response.status_code == 200
        body = response.json()
        assert len(body) == 1
        assert body[0]["service"] == "api"

    async def test_returns_404_when_project_not_found(self, api_client, auth_headers, mocker):
        mocker.patch("app.routers.metrics.load_project", return_value=None)
        async with api_client() as client:
            response = await client.get("/api/projects/unknown/metrics", headers=auth_headers())
        assert response.status_code == 404

    async def test_returns_401_without_token(self, api_client):
        async with api_client() as client:
            response = await client.get("/api/projects/my-project/metrics")
        assert response.status_code == 401
