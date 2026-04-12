from httpx import ASGITransport
from httpx import AsyncClient

from app.main import app


class TestPing:
    """Tests for the /api health check endpoint."""

    async def test_ping_returns_ok(self):
        """Health check endpoint returns 200 with status ok.

        Given: The FastAPI application is running
        When: GET /api
        Then: Should return 200 with {"status": "ok"}
        """
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api")

        assert response.status_code == 200, f"Expected 200 but got {response.status_code=}"
        data = response.json()
        assert data == {"status": "ok"}, f"Expected ok payload but got {data=}"
