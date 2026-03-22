import pytest

from app.constants import AlertLevel, ContainerState, DockerComposeLabel, HealthState
from app.services.alerts_service import Alert, AlertsService


class TestAlertsService:
    """Unit tests for AlertsService."""

    class TestAlertsForContainer:
        """Tests for _alerts_for_container()."""

        def test_returns_empty_list_when_no_project_label(self, mocker):
            """Return empty list for containers without a project label.

            Given: A container with no docker-compose project label
            When: Calling _alerts_for_container()
            Then: Should return an empty list
            """
            container = mocker.MagicMock()
            container.labels = {}

            service = AlertsService()
            result = service._alerts_for_container(container)

            assert result == [], f"Expected empty list but got {result=}"

        def test_generates_critical_alert_for_failed_exit(self, mocker):
            """Generate a CRITICAL alert for a container that exited with non-zero code.

            Given: A stopped container with exit code 1
            When: Calling _alerts_for_container()
            Then: Should return one CRITICAL alert
            """
            container = mocker.MagicMock()
            container.short_id = "abc123"
            container.name = "myproject_web_1"
            container.status = ContainerState.EXITED
            container.labels = {
                DockerComposeLabel.PROJECT: "myproject",
                DockerComposeLabel.SERVICE: "web",
            }
            container.attrs = {"State": {"ExitCode": 1, "Health": {}}}

            service = AlertsService()
            result = service._alerts_for_container(container)

            assert len(result) == 1, f"Expected 1 alert but got {len(result)=}"
            assert result[0].level == AlertLevel.CRITICAL, f"Expected CRITICAL but got {result[0].level=}"
            assert "1" in result[0].message, f"Exit code not in message: {result[0].message=}"

        def test_generates_info_alert_for_clean_exit(self, mocker):
            """Generate an INFO alert for a container that exited with code 0.

            Given: A stopped container with exit code 0
            When: Calling _alerts_for_container()
            Then: Should return one INFO alert
            """
            container = mocker.MagicMock()
            container.short_id = "abc123"
            container.name = "myproject_web_1"
            container.status = ContainerState.EXITED
            container.labels = {
                DockerComposeLabel.PROJECT: "myproject",
                DockerComposeLabel.SERVICE: "web",
            }
            container.attrs = {"State": {"ExitCode": 0, "Health": {}}}

            service = AlertsService()
            result = service._alerts_for_container(container)

            assert len(result) == 1, f"Expected 1 alert but got {len(result)=}"
            assert result[0].level == AlertLevel.INFO, f"Expected INFO but got {result[0].level=}"

        def test_generates_warning_alert_for_restarting_container(self, mocker):
            """Generate a WARNING alert for a restarting container.

            Given: A container in RESTARTING state
            When: Calling _alerts_for_container()
            Then: Should return one WARNING alert
            """
            container = mocker.MagicMock()
            container.short_id = "abc123"
            container.name = "myproject_web_1"
            container.status = ContainerState.RESTARTING
            container.labels = {
                DockerComposeLabel.PROJECT: "myproject",
                DockerComposeLabel.SERVICE: "web",
            }
            container.attrs = {"State": {"Health": {}}}

            service = AlertsService()
            result = service._alerts_for_container(container)

            assert len(result) == 1, f"Expected 1 alert but got {len(result)=}"
            assert result[0].level == AlertLevel.WARNING, f"Expected WARNING but got {result[0].level=}"

        def test_generates_critical_alert_for_unhealthy_container(self, mocker):
            """Generate a CRITICAL alert for a container with failing healthcheck.

            Given: A running container with healthcheck status = unhealthy
            When: Calling _alerts_for_container()
            Then: Should return one CRITICAL alert for the healthcheck failure
            """
            container = mocker.MagicMock()
            container.short_id = "abc123"
            container.name = "myproject_web_1"
            container.status = ContainerState.RUNNING
            container.labels = {
                DockerComposeLabel.PROJECT: "myproject",
                DockerComposeLabel.SERVICE: "web",
            }
            container.attrs = {"State": {"Health": {"Status": HealthState.UNHEALTHY}}}

            service = AlertsService()
            result = service._alerts_for_container(container)

            assert len(result) == 1, f"Expected 1 alert but got {len(result)=}"
            assert result[0].level == AlertLevel.CRITICAL, f"Expected CRITICAL but got {result[0].level=}"
            assert "health" in result[0].id, f"Expected health alert id but got {result[0].id=}"

        def test_generates_no_alerts_for_healthy_running_container(self, mocker):
            """Return no alerts for a healthy running container.

            Given: A running container with no health issues
            When: Calling _alerts_for_container()
            Then: Should return an empty list
            """
            container = mocker.MagicMock()
            container.short_id = "abc123"
            container.name = "myproject_web_1"
            container.status = ContainerState.RUNNING
            container.labels = {
                DockerComposeLabel.PROJECT: "myproject",
                DockerComposeLabel.SERVICE: "web",
            }
            container.attrs = {"State": {"Health": {"Status": "healthy"}}}

            service = AlertsService()
            result = service._alerts_for_container(container)

            assert result == [], f"Expected empty list but got {result=}"

    class TestGetAll:
        """Tests for get_all()."""

        def test_returns_all_alerts_across_containers(self, mocker):
            """Return alerts from all containers using mocked Docker client.

            Given: Two containers, one with an alert and one healthy
            When: Calling get_all()
            Then: Should return only the alerts from the first container
            """
            c1 = mocker.MagicMock()
            c1.short_id = "abc"
            c1.status = ContainerState.EXITED
            c1.labels = {DockerComposeLabel.PROJECT: "proj1", DockerComposeLabel.SERVICE: "web"}
            c1.attrs = {"State": {"ExitCode": 1, "Health": {}}}

            c2 = mocker.MagicMock()
            c2.short_id = "def"
            c2.status = ContainerState.RUNNING
            c2.labels = {DockerComposeLabel.PROJECT: "proj2", DockerComposeLabel.SERVICE: "db"}
            c2.attrs = {"State": {"Health": {}}}

            mock_client = mocker.MagicMock()
            mock_client.containers.list.return_value = [c1, c2]
            mocker.patch("app.services.alerts_service.docker_client.client", return_value=mock_client)

            service = AlertsService()
            result = service.get_all()

            assert len(result) == 1, f"Expected 1 alert but got {len(result)=}"
            assert result[0].project == "proj1", f"Expected proj1 but got {result[0].project=}"

        def test_returns_empty_list_on_docker_exception(self, mocker):
            """Return empty list when Docker is unavailable.

            Given: Docker daemon is not reachable (raises DockerException)
            When: Calling get_all()
            Then: Should return an empty list without raising
            """
            import docker.errors

            mock_client = mocker.MagicMock()
            mock_client.containers.list.side_effect = docker.errors.DockerException("Docker down")
            mocker.patch("app.services.alerts_service.docker_client.client", return_value=mock_client)

            service = AlertsService()
            result = service.get_all()

            assert result == [], f"Expected empty list but got {result=}"

    class TestGetForProject:
        """Tests for get_for_project()."""

        def test_filters_alerts_by_project(self, mocker):
            """Return only alerts matching the requested project.

            Given: get_all() returning alerts from two different projects
            When: Calling get_for_project("proj1")
            Then: Should return only the alert for proj1
            """
            alert1 = Alert(
                id="x-exited", level=AlertLevel.CRITICAL,
                project="proj1", service="web",
                message="stopped", timestamp="2026-01-01T00:00:00+00:00",
            )
            alert2 = Alert(
                id="y-exited", level=AlertLevel.INFO,
                project="proj2", service="api",
                message="stopped", timestamp="2026-01-01T00:00:00+00:00",
            )
            mocker.patch.object(AlertsService, "get_all", return_value=[alert1, alert2])

            service = AlertsService()
            result = service.get_for_project("proj1")

            assert len(result) == 1, f"Expected 1 alert but got {len(result)=}"
            assert result[0].project == "proj1", f"Expected proj1 but got {result[0].project=}"
