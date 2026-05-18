from unittest.mock import MagicMock

from app.routers.alerts import _container_alerts
from docker.errors import DockerException


def _make_container(
    *,
    short_id: str = "abc123",
    name: str = "web_1",
    status: str = "running",
    project: str = "myproject",
    service: str = "web",
    exit_code: int = 0,
    health_status: str | None = None,
) -> MagicMock:
    container = MagicMock()
    container.short_id = short_id
    container.name = name
    container.status = status
    container.labels = {
        "com.docker.compose.project": project,
        "com.docker.compose.service": service,
    }
    state: dict = {"ExitCode": exit_code}
    if health_status:
        state["Health"] = {"Status": health_status}
    container.attrs = {"State": state}
    return container


class TestContainerAlerts:
    """Unit tests for _container_alerts() helper."""

    def test_returns_empty_when_no_containers(self, mocker):
        """Return empty list when Docker reports no containers."""
        mock_client = MagicMock()
        mock_client.containers.list.return_value = []
        mocker.patch("app.routers.alerts.get_docker_client", return_value=mock_client)

        result = _container_alerts()

        assert result == []

    def test_skips_containers_without_project_label(self, mocker):
        """Skip containers that have no compose project label."""
        container = MagicMock()
        container.labels = {}
        container.status = "running"
        container.attrs = {"State": {}}
        mock_client = MagicMock()
        mock_client.containers.list.return_value = [container]
        mocker.patch("app.routers.alerts.get_docker_client", return_value=mock_client)

        result = _container_alerts()

        assert result == []

    def test_exited_with_nonzero_code_creates_critical_alert(self, mocker):
        """Exited container with exit code != 0 should generate a critical alert."""
        container = _make_container(status="exited", exit_code=1)
        mock_client = MagicMock()
        mock_client.containers.list.return_value = [container]
        mocker.patch("app.routers.alerts.get_docker_client", return_value=mock_client)

        result = _container_alerts()

        assert len(result) == 1
        assert result[0].level == "critical"
        assert result[0].id == "abc123-exited"

    def test_exited_with_zero_code_creates_info_alert(self, mocker):
        """Exited container with exit code 0 should generate an info alert."""
        container = _make_container(status="exited", exit_code=0)
        mock_client = MagicMock()
        mock_client.containers.list.return_value = [container]
        mocker.patch("app.routers.alerts.get_docker_client", return_value=mock_client)

        result = _container_alerts()

        assert len(result) == 1
        assert result[0].level == "info"

    def test_restarting_container_creates_warning_alert(self, mocker):
        """Restarting container should generate a warning alert."""
        container = _make_container(status="restarting")
        mock_client = MagicMock()
        mock_client.containers.list.return_value = [container]
        mocker.patch("app.routers.alerts.get_docker_client", return_value=mock_client)

        result = _container_alerts()

        assert len(result) == 1
        assert result[0].level == "warning"
        assert result[0].id == "abc123-restart"

    def test_unhealthy_container_creates_critical_health_alert(self, mocker):
        """Container with unhealthy healthcheck should generate a critical alert."""
        container = _make_container(health_status="unhealthy")
        mock_client = MagicMock()
        mock_client.containers.list.return_value = [container]
        mocker.patch("app.routers.alerts.get_docker_client", return_value=mock_client)

        result = _container_alerts()

        assert len(result) == 1
        assert result[0].level == "critical"
        assert result[0].id == "abc123-health"

    def test_starting_health_creates_info_alert(self, mocker):
        """Container with healthcheck in starting state should generate an info alert."""
        container = _make_container(health_status="starting")
        mock_client = MagicMock()
        mock_client.containers.list.return_value = [container]
        mocker.patch("app.routers.alerts.get_docker_client", return_value=mock_client)

        result = _container_alerts()

        assert len(result) == 1
        assert result[0].level == "info"
        assert result[0].id == "abc123-starting"

    def test_uses_container_name_when_no_service_label(self, mocker):
        """Use container.name as service when service label is absent."""
        container = MagicMock()
        container.short_id = "def456"
        container.name = "standalone_container"
        container.status = "restarting"
        container.labels = {"com.docker.compose.project": "myproject"}
        container.attrs = {"State": {}}
        mock_client = MagicMock()
        mock_client.containers.list.return_value = [container]
        mocker.patch("app.routers.alerts.get_docker_client", return_value=mock_client)

        result = _container_alerts()

        assert result[0].service == "standalone_container"

    def test_suppresses_docker_exception(self, mocker):
        """Return empty list when Docker raises DockerException."""
        mocker.patch("app.routers.alerts.get_docker_client", side_effect=DockerException("unreachable"))

        result = _container_alerts()

        assert result == []

    def test_multiple_alerts_for_one_container(self, mocker):
        """Exited (critical) + unhealthy health should produce two alerts."""
        container = _make_container(status="exited", exit_code=1, health_status="unhealthy")
        mock_client = MagicMock()
        mock_client.containers.list.return_value = [container]
        mocker.patch("app.routers.alerts.get_docker_client", return_value=mock_client)

        result = _container_alerts()

        assert len(result) == 2
        levels = {a.level for a in result}
        assert "critical" in levels
