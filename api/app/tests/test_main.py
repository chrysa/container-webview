from fastapi import status
from httpx import ASGITransport
from httpx import AsyncClient

from app.main import app


class TestHealth:
    """Tests for the /health liveness endpoint."""

    async def test_health_returns_ok(self):
        """Health check endpoint returns 200 with status ok.

        Given: The FastAPI application is running
        When: GET /health
        Then: Should return 200 with a payload whose status is "ok"
        """
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/health")

        assert response.status_code == status.HTTP_200_OK, (
            f"Expected 200 but got {response.status_code=}"
        )
        data = response.json()
        assert data["status"] == "ok", f"Expected ok status but got {data=}"
