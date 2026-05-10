import pytest

from app.services.project_manager import _normalize_environment
from app.services.project_manager import _normalize_ports
from app.services.project_manager import _safe_project_path
from app.services.project_manager import load_project


class TestSafeProjectPath:
    """Tests for _safe_project_path() path-traversal guard."""

    def test_returns_valid_path(self, tmp_path, mocker):
        """Return resolved path for a valid project id.

        Given: A base projects directory and a simple project id
        When: Calling _safe_project_path("myproject")
        Then: Should return the resolved path without raising
        """
        mocker.patch("app.services.project_manager.settings", projects_path=str(tmp_path))
        result = _safe_project_path("myproject")
        assert str(result).startswith(str(tmp_path)), f"Expected path under {tmp_path} but got {result=}"

    def test_raises_on_path_traversal(self, tmp_path, mocker):
        """Raise ValueError when project id contains path traversal characters.

        Given: A project id with "../" that escapes the base directory
        When: Calling _safe_project_path("../../etc/passwd")
        Then: Should raise ValueError
        """
        mocker.patch("app.services.project_manager.settings", projects_path=str(tmp_path))

        with pytest.raises(ValueError):
            _safe_project_path("../../etc/passwd")


class TestNormalizePorts:
    """Tests for _normalize_ports() function."""

    def test_returns_empty_list_for_none(self):
        """Return empty list when ports is None.

        Given: None as raw ports value
        When: Calling _normalize_ports(None)
        Then: Should return []
        """
        result = _normalize_ports(None)
        assert result == [], f"Expected [] but got {result=}"

    def test_normalizes_string_ports(self):
        """Return string ports unchanged.

        Given: A list of port strings
        When: Calling _normalize_ports(["8080:80", "443:443"])
        Then: Should return the same list as strings
        """
        result = _normalize_ports(["8080:80", "443:443"])
        assert result == ["8080:80", "443:443"], f"Expected port strings but got {result=}"

    def test_normalizes_dict_ports(self):
        """Extract 'target' key from dict-format port specs.

        Given: A list of dict port specs with target key
        When: Calling _normalize_ports([{"target": 80}])
        Then: Should return ["80"]
        """
        result = _normalize_ports([{"target": 80, "published": 8080}])
        assert result == ["80"], f"Expected ['80'] but got {result=}"


class TestNormalizeEnvironment:
    """Tests for _normalize_environment() function."""

    def test_returns_empty_dict_for_none(self):
        """Return empty dict for None environment.

        Given: None as raw environment value
        When: Calling _normalize_environment(None)
        Then: Should return {}
        """
        result = _normalize_environment(None)
        assert result == {}, f"Expected {{}} but got {result=}"

    def test_normalizes_dict_environment(self):
        """Return dict environment as-is, stringifying values.

        Given: A dict with string key-value pairs
        When: Calling _normalize_environment({"KEY": "value"})
        Then: Should return the same dict
        """
        result = _normalize_environment({"KEY": "value", "PORT": 8000})
        assert result["KEY"] == "value", f"Expected 'value' but got {result['KEY']=}"
        assert result["PORT"] == "8000", f"Expected '8000' but got {result['PORT']=}"

    def test_normalizes_list_environment(self):
        """Parse KEY=VALUE list format into a dict.

        Given: A list of "KEY=value" strings
        When: Calling _normalize_environment(["KEY=value", "PORT=8000"])
        Then: Should return {"KEY": "value", "PORT": "8000"}
        """
        result = _normalize_environment(["KEY=value", "PORT=8000"])
        assert result == {"KEY": "value", "PORT": "8000"}, f"Expected parsed env but got {result=}"


class TestLoadProject:
    """Tests for load_project()."""

    def test_returns_none_for_missing_directory(self, tmp_path, mocker):
        """Return None when the project directory does not exist.

        Given: A projects_path with no subdirectory matching the project id
        When: Calling load_project("nonexistent")
        Then: Should return None
        """
        mocker.patch("app.services.project_manager.settings", projects_path=str(tmp_path))
        result = load_project("nonexistent")
        assert result is None, f"Expected None but got {result=}"

    def test_returns_none_for_path_traversal(self, tmp_path, mocker):
        """Return None when project id attempts path traversal.

        Given: A project id with path traversal characters
        When: Calling load_project("../../etc")
        Then: Should return None (not raise)
        """
        mocker.patch("app.services.project_manager.settings", projects_path=str(tmp_path))
        result = load_project("../../etc")
        assert result is None, f"Expected None for traversal attempt but got {result=}"

    def test_returns_none_when_no_compose_file(self, tmp_path, mocker):
        """Return None when directory has no docker-compose file.

        Given: A project directory with no supported compose file
        When: Calling load_project("emptyproject")
        Then: Should return None
        """
        project_dir = tmp_path / "emptyproject"
        project_dir.mkdir()
        mocker.patch("app.services.project_manager.settings", projects_path=str(tmp_path))
        result = load_project("emptyproject")
        assert result is None, f"Expected None but got {result=}"

    def test_loads_project_from_compose_file(self, tmp_path, mocker):
        """Return a ProjectModel parsed from a valid docker-compose.yml.

        Given: A project directory with a docker-compose.yml containing one service
        When: Calling load_project("myproject")
        Then: Should return a ProjectModel with the service populated
        """
        project_dir = tmp_path / "myproject"
        project_dir.mkdir()
        compose_content = """\
services:
  web:
    image: nginx:alpine
    ports:
      - "80:80"
networks:
  default:
"""
        (project_dir / "docker-compose.yml").write_text(compose_content)
        mocker.patch("app.services.project_manager.settings", projects_path=str(tmp_path))
        result = load_project("myproject")

        assert result is not None, "Expected ProjectModel but got None"
        assert result.id == "myproject", f"Expected 'myproject' but got {result.id=}"
        assert len(result.services) == 1, f"Expected 1 service but got {len(result.services)=}"
        assert result.services[0].name == "web", f"Expected 'web' but got {result.services[0].name=}"
        assert result.services[0].image == "nginx:alpine", (
            f"Expected 'nginx:alpine' but got {result.services[0].image=}"
        )
