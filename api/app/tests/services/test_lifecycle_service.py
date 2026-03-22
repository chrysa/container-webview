import pytest

from app.constants import ERR_CONTAINER_NOT_FOUND, ERR_PROJECT_NOT_FOUND, ERR_SERVICE_NOT_FOUND, ERR_UNKNOWN_ACTION
from app.services.lifecycle_service import LifecycleService


class TestLifecycleService:
    """Unit tests for LifecycleService."""

    class TestPerformValidation:
        """Tests for action/project/service validation."""

        def test_raises_for_unknown_action(self, mocker):
            """Raise ValueError for an unrecognised lifecycle action.

            Given: A valid project and service but an unknown action name
            When: Calling perform() with action="fly"
            Then: Should raise ValueError with ERR_UNKNOWN_ACTION message
            """
            service = LifecycleService()

            with pytest.raises(ValueError, match="Unknown action") as exc_info:
                service.perform("myproject", "web", "fly")

            assert ERR_UNKNOWN_ACTION.format("fly") in str(exc_info.value), (
                f"Expected ERR_UNKNOWN_ACTION but got {exc_info.value=}"
            )

        def test_raises_when_project_not_found(self, mocker):
            """Raise ValueError when the project does not exist.

            Given: A project that cannot be loaded by ProjectManager
            When: Calling perform() with a valid action
            Then: Should raise ValueError with ERR_PROJECT_NOT_FOUND
            """
            mocker.patch("app.services.lifecycle_service.project_manager.load", return_value=None)

            service = LifecycleService()

            with pytest.raises(ValueError) as exc_info:
                service.perform("missing", "web", "start")

            assert ERR_PROJECT_NOT_FOUND in str(exc_info.value), (
                f"Expected ERR_PROJECT_NOT_FOUND but got {exc_info.value=}"
            )

        def test_raises_when_service_not_found(self, mocker):
            """Raise ValueError when the service name is not in the project.

            Given: A project with a single service "db"
            When: Calling perform() for service "web" (not in project)
            Then: Should raise ValueError with ERR_SERVICE_NOT_FOUND
            """
            mock_service = mocker.MagicMock()
            mock_service.name = "db"
            mock_project = mocker.MagicMock()
            mock_project.services = [mock_service]
            mocker.patch("app.services.lifecycle_service.project_manager.load", return_value=mock_project)

            service = LifecycleService()

            with pytest.raises(ValueError) as exc_info:
                service.perform("myproject", "web", "start")

            assert ERR_SERVICE_NOT_FOUND.format("web") in str(exc_info.value), (
                f"Expected ERR_SERVICE_NOT_FOUND but got {exc_info.value=}"
            )

        def test_raises_when_container_not_found(self, mocker):
            """Raise ValueError when the container is not running.

            Given: A valid project+service but no running Docker container
            When: Calling perform() with action="stop"
            Then: Should raise ValueError with ERR_CONTAINER_NOT_FOUND
            """
            mock_svc = mocker.MagicMock()
            mock_svc.name = "web"
            mock_project = mocker.MagicMock()
            mock_project.services = [mock_svc]
            mocker.patch("app.services.lifecycle_service.project_manager.load", return_value=mock_project)
            mocker.patch("app.services.lifecycle_service.docker_client.get_container_for_service", return_value=None)

            service = LifecycleService()

            with pytest.raises(ValueError) as exc_info:
                service.perform("myproject", "web", "stop")

            assert ERR_CONTAINER_NOT_FOUND.format("web") in str(exc_info.value), (
                f"Expected ERR_CONTAINER_NOT_FOUND but got {exc_info.value=}"
            )

    class TestPerformActions:
        """Tests for successful lifecycle action execution."""

        @pytest.mark.parametrize("action", ["start", "stop", "restart", "pause", "unpause", "kill"])
        def test_performs_valid_action_and_returns_status(self, mocker, action):
            """Execute a valid action and return the post-action container status.

            Given: A valid project, service, and running container
            When: Calling perform() with a valid action
            Then: Should call the action on the container and return its new status
            """
            mock_svc = mocker.MagicMock()
            mock_svc.name = "web"
            mock_project = mocker.MagicMock()
            mock_project.services = [mock_svc]
            mock_container = mocker.MagicMock()
            mock_container.status = "running"

            mocker.patch("app.services.lifecycle_service.project_manager.load", return_value=mock_project)
            mocker.patch(
                "app.services.lifecycle_service.docker_client.get_container_for_service",
                return_value=mock_container,
            )

            service = LifecycleService()
            result = service.perform("myproject", "web", action)

            getattr(mock_container, action).assert_called_once(), (
                f"Expected {action}() to be called on container"
            )
            mock_container.reload.assert_called_once(), "Container.reload() should be called after action"
            assert result == mock_container.status, f"Expected container status but got {result=}"
