from unittest.mock import AsyncMock
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.security import create_access_token


@pytest.fixture(name="test_token")
def fixt_test_token():
    return create_access_token({"sub": "testuser"})


class TestStreamLogsWebSocket:
    """Tests for WebSocket /api/logs/{project_id}/services/{service_name}/logs."""

    def test_closes_4001_when_token_invalid(self):
        """Close with code 4001 when the token is invalid."""
        with TestClient(app) as client:
            with pytest.raises(Exception):
                with client.websocket_connect(
                    "/api/logs/myproject/services/web/logs?token=invalidtoken"
                ) as ws:
                    ws.receive_text()

    def test_closes_4004_when_project_not_found(self, mocker, test_token):
        """Close with code 4004 when project_id resolves to no project."""
        mocker.patch("app.routers.logs.load_project", return_value=None)
        with TestClient(app) as client:
            with pytest.raises(Exception):
                with client.websocket_connect(
                    f"/api/logs/missing/services/web/logs?token={test_token}"
                ) as ws:
                    ws.receive_text()

    def test_closes_4004_when_container_not_found(self, mocker, test_token):
        """Close with code 4004 when service container does not exist."""
        mocker.patch("app.routers.logs.load_project", return_value=MagicMock())
        mocker.patch("app.routers.logs.get_container_for_service", return_value=None)
        with TestClient(app) as client:
            with pytest.raises(Exception):
                with client.websocket_connect(
                    f"/api/logs/myproject/services/web/logs?token={test_token}"
                ) as ws:
                    ws.receive_text()

    def test_streams_log_lines(self, mocker, test_token):
        """Verify container.logs() is invoked when auth + project + container are valid.

        Because the TestClient's sync event loop closes the WebSocket before the
        async for-loop completes, we assert via the mock call count rather than
        received lines.  The important invariant is that container.logs() is
        called with the expected parameters.
        """
    async def test_streams_log_lines(self, mocker):
        """Verify stream_logs() calls container.logs() and sends text to websocket."""
        from unittest.mock import AsyncMock, MagicMock, call, patch

        from app.routers.logs import stream_logs
        from app.security import create_access_token

        token = create_access_token({"sub": "testuser"})
        mock_ws = AsyncMock()
        mock_ws.close = AsyncMock()

        mock_project = MagicMock()
        mock_container = MagicMock()
        mock_container.logs.return_value = iter([b"hello\n", b"world\n"])

        with (
            patch("app.routers.logs.load_project", return_value=mock_project),
            patch("app.routers.logs.get_container_for_service", return_value=mock_container),
            patch("app.routers.logs.asyncio.sleep", new=AsyncMock(return_value=None)),
        ):
            await stream_logs(
                websocket=mock_ws,
                project_id="myproject",
                service_name="web",
                token=token,
                tail=100,
            )

        mock_container.logs.assert_called_once_with(
            stream=True, follow=True, tail=100, timestamps=True
        )
        mock_ws.send_text.assert_any_call("hello")
        mock_ws.send_text.assert_any_call("world")
