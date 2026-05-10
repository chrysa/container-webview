from app.constants import DockerComposeLabel
from app.services.docker_client import get_all_containers_for_project
from app.services.docker_client import get_container_for_service


class TestGetContainerForService:
    """Tests for get_container_for_service()."""

    def test_returns_matching_container(self, mocker):
        """Return the container that matches project + service labels.

        Given: Two containers, only one matching the target project and service
        When: Calling get_container_for_service(project_id, service_name)
        Then: Should return the matching container
        """
        target = mocker.MagicMock()
        target.labels = {
            DockerComposeLabel.PROJECT: "myproject",
            DockerComposeLabel.SERVICE: "web",
        }
        other = mocker.MagicMock()
        other.labels = {
            DockerComposeLabel.PROJECT: "other",
            DockerComposeLabel.SERVICE: "db",
        }
        mock_client = mocker.MagicMock()
        mock_client.containers.list.return_value = [other, target]
        mocker.patch("app.services.docker_client.get_docker_client", return_value=mock_client)

        result = get_container_for_service("myproject", "web")

        assert result is target, f"Expected target container but got {result=}"

    def test_returns_none_when_no_match(self, mocker):
        """Return None when no container matches the given project and service.

        Given: A running container from a different project
        When: Calling get_container_for_service with a project that has no containers
        Then: Should return None
        """
        other = mocker.MagicMock()
        other.labels = {
            DockerComposeLabel.PROJECT: "other",
            DockerComposeLabel.SERVICE: "web",
        }
        mock_client = mocker.MagicMock()
        mock_client.containers.list.return_value = [other]
        mocker.patch("app.services.docker_client.get_docker_client", return_value=mock_client)

        result = get_container_for_service("myproject", "web")

        assert result is None, f"Expected None but got {result=}"

    def test_returns_none_when_empty_list(self, mocker):
        """Return None when Docker reports no containers at all.

        Given: No running or stopped containers
        When: Calling get_container_for_service
        Then: Should return None
        """
        mock_client = mocker.MagicMock()
        mock_client.containers.list.return_value = []
        mocker.patch("app.services.docker_client.get_docker_client", return_value=mock_client)

        result = get_container_for_service("myproject", "web")

        assert result is None, f"Expected None but got {result=}"


class TestGetAllContainersForProject:
    """Tests for get_all_containers_for_project()."""

    def test_returns_only_project_containers(self, mocker):
        """Return only containers belonging to the specified project.

        Given: Three containers, two belonging to myproject and one to another project
        When: Calling get_all_containers_for_project("myproject")
        Then: Should return the two myproject containers only
        """
        c1 = mocker.MagicMock()
        c1.labels = {DockerComposeLabel.PROJECT: "myproject"}
        c2 = mocker.MagicMock()
        c2.labels = {DockerComposeLabel.PROJECT: "myproject"}
        c3 = mocker.MagicMock()
        c3.labels = {DockerComposeLabel.PROJECT: "other"}

        mock_client = mocker.MagicMock()
        mock_client.containers.list.return_value = [c1, c2, c3]
        mocker.patch("app.services.docker_client.get_docker_client", return_value=mock_client)

        result = get_all_containers_for_project("myproject")

        assert len(result) == 2, f"Expected 2 containers but got {len(result)=}"
        assert c1 in result, "c1 should be in results"
        assert c2 in result, "c2 should be in results"
        assert c3 not in result, "c3 from another project should not be included"

    def test_returns_empty_list_when_no_match(self, mocker):
        """Return empty list when project has no containers.

        Given: No containers matching the target project
        When: Calling get_all_containers_for_project
        Then: Should return an empty list
        """
        mock_client = mocker.MagicMock()
        mock_client.containers.list.return_value = []
        mocker.patch("app.services.docker_client.get_docker_client", return_value=mock_client)

        result = get_all_containers_for_project("myproject")

        assert result == [], f"Expected empty list but got {result=}"
