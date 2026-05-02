import pytest

<<<<<<< HEAD

class TestNormalizePorts:
    """Unit tests for _normalize_ports()."""

    def test_returns_empty_list_when_none(self):
        """Return empty list when ports_raw is None.

        Given: ports_raw is None
        When: calling _normalize_ports(None)
        Then: should return []
        """
        from app.services.project_manager import _normalize_ports

        result = _normalize_ports(None)
        assert result == [], f"Expected [] but got {result=}"

    def test_returns_string_ports_as_is(self):
        """Convert string port entries to string list.

        Given: list of string ports like ["80:80", "443:443"]
        When: calling _normalize_ports
        Then: should return the same values as strings
        """
        from app.services.project_manager import _normalize_ports

        result = _normalize_ports(["80:80", "443:443"])
        assert result == ["80:80", "443:443"], f"Unexpected {result=}"

    def test_extracts_target_from_dict_ports(self):
        """Extract target port from dict-format port entries.

        Given: list of dict ports with 'target' key
        When: calling _normalize_ports
        Then: should return the target values as strings
        """
        from app.services.project_manager import _normalize_ports

        result = _normalize_ports([{"target": 80, "published": 8080}])
        assert result == ["80"], f"Unexpected {result=}"


class TestNormalizeDepends:
    """Unit tests for _normalize_depends()."""

    @pytest.mark.parametrize(
        "raw,expected",
        [
            (None, []),
            ([], []),
            (["db", "cache"], ["db", "cache"]),
            ({"db": {"condition": "service_healthy"}, "cache": {}}, ["db", "cache"]),
        ],
    )
    def test_various_formats(self, raw, expected):
        """Parse depends_on in both list and dict formats.

        Given: depends_on value in various YAML formats
        When: calling _normalize_depends
        Then: should always return a flat list of service names
        """
        from app.services.project_manager import _normalize_depends

        result = _normalize_depends(raw)
        assert result == expected, f"For {raw=} expected {expected=} but got {result=}"


class TestNormalizeEnvironment:
    """Unit tests for _normalize_environment()."""

    def test_returns_empty_dict_when_none(self):
        """Return empty dict when env_raw is None.

        Given: env_raw is None
        When: calling _normalize_environment
        Then: should return {}
        """
        from app.services.project_manager import _normalize_environment

        result = _normalize_environment(None)
        assert result == {}, f"Expected {{}} but got {result=}"

    def test_parses_dict_format(self):
        """Parse environment as dict.

        Given: environment as a dict
        When: calling _normalize_environment
        Then: should return dict with values converted to strings
        """
        from app.services.project_manager import _normalize_environment

        result = _normalize_environment({"PORT": 8080, "DEBUG": True})
        assert result == {"PORT": "8080", "DEBUG": "True"}, f"Unexpected {result=}"

    def test_parses_list_format(self):
        """Parse environment as KEY=VALUE list.

        Given: environment as list of KEY=VALUE strings
        When: calling _normalize_environment
        Then: should return the corresponding dict
        """
        from app.services.project_manager import _normalize_environment

        result = _normalize_environment(["PORT=8080", "DEBUG=true"])
        assert result == {"PORT": "8080", "DEBUG": "true"}, f"Unexpected {result=}"

    def test_skips_none_values_in_dict(self):
        """Skip entries with None values.

        Given: environment dict containing None values
        When: calling _normalize_environment
        Then: should omit keys with None values
        """
        from app.services.project_manager import _normalize_environment

        result = _normalize_environment({"A": "yes", "B": None})
        assert "B" not in result, f"Expected 'B' to be omitted but got {result=}"
        assert result.get("A") == "yes", f"Expected A=yes but got {result=}"


class TestLoadProject:
    """Unit tests for load_project()."""

    def test_returns_none_for_path_traversal(self, mocker):
        """Reject path traversal project IDs.

        Given: A project id with '..' components
        When: calling load_project('../etc/passwd')
        Then: should return None without raising
        """
        mocker.patch("app.services.project_manager.settings")
        from app.services.project_manager import load_project

        result = load_project("../etc/passwd")
        assert result is None, f"Expected None for path traversal but got {result=}"

    def test_returns_none_when_directory_missing(self, tmp_path, mocker):
        """Return None when project directory does not exist.

        Given: A project id pointing to a non-existent directory
        When: calling load_project
        Then: should return None
        """
        mock_settings = mocker.patch("app.services.project_manager.settings")
        mock_settings.projects_path = str(tmp_path)

        result = load_project("nonexistent")
        assert result is None, f"Expected None for missing dir but got {result=}"

    def test_returns_none_when_no_compose_file(self, tmp_path, mocker):
        """Return None when project directory has no compose file.

        Given: A project directory exists but contains no docker-compose.yml
        When: calling load_project
        Then: should return None
        """
        mock_settings = mocker.patch("app.services.project_manager.settings")
        mock_settings.projects_path = str(tmp_path)
        project_dir = tmp_path / "my-project"
        project_dir.mkdir()

        result = load_project("my-project")
        assert result is None, f"Expected None for missing compose file but got {result=}"

    def test_parses_valid_compose_file(self, tmp_path, mocker):
        """Parse a valid docker-compose.yml and return a ProjectModel.

        Given: A project directory with a valid docker-compose.yml
        When: calling load_project
        Then: should return a ProjectModel with correct services
        """
        mock_settings = mocker.patch("app.services.project_manager.settings")
        mock_settings.projects_path = str(tmp_path)

        project_dir = tmp_path / "myapp"
        project_dir.mkdir()
        compose = project_dir / "docker-compose.yml"
        compose.write_text(
            "services:\n  web:\n    image: nginx:latest\n    ports:\n      - '80:80'\n  db:\n    image: postgres:15\n"
        )

        result = load_project("myapp")

        assert result is not None, "Expected a ProjectModel but got None"
        assert result.id == "myapp", f"Unexpected {result.id=}"
        service_names = [s.name for s in result.services]
        assert "web" in service_names, f"Expected 'web' in services but got {service_names=}"
        assert "db" in service_names, f"Expected 'db' in services but got {service_names=}"
||||||| parent of 62afd77 (test(api): add unit tests, fix guidelines violations, update docs\n\n- Single outer test class with nested sub-classes (no multiple module-level classes)\n- No type annotations in test helpers or factory functions\n- No imports inside fixture/method bodies\n- No noqa comments\n- mocker.patch for all mocking, Given-When-Then docstrings\n- conftest: move security import to module level\n- docs: rewrite README, update changelog, fix stale make targets")
=======
from app.services.project_manager import ProjectManager, ProjectModel, ServiceModel


class TestProjectManager:
    """Unit tests for ProjectManager."""

    class TestSafeProjectPath:
        """Tests for _safe_project_path() path-traversal guard."""

        def test_returns_valid_path(self, tmp_path, mocker):
            """Return resolved path for a valid project id.

            Given: A base projects directory and a simple project id
            When: Calling _safe_project_path("myproject")
            Then: Should return the resolved path without raising
            """
            mocker.patch(
                "app.services.project_manager.get_settings",
                return_value=mocker.MagicMock(projects_path=str(tmp_path)),
            )
            manager = ProjectManager()
            result = manager._safe_project_path("myproject")
            assert str(result).startswith(str(tmp_path)), (
                f"Expected path under {tmp_path} but got {result=}"
            )

        def test_raises_on_path_traversal(self, tmp_path, mocker):
            """Raise ValueError when project id contains path traversal characters.

            Given: A project id with "../" that escapes the base directory
            When: Calling _safe_project_path("../../etc/passwd")
            Then: Should raise ValueError
            """
            mocker.patch(
                "app.services.project_manager.get_settings",
                return_value=mocker.MagicMock(projects_path=str(tmp_path)),
            )
            manager = ProjectManager()

            with pytest.raises(ValueError):
                manager._safe_project_path("../../etc/passwd")

    class TestNormalizePorts:
        """Tests for _normalize_ports() static method."""

        def test_returns_empty_list_for_none(self):
            """Return empty list when ports is None.

            Given: None as raw ports value
            When: Calling _normalize_ports(None)
            Then: Should return []
            """
            result = ProjectManager._normalize_ports(None)
            assert result == [], f"Expected [] but got {result=}"

        def test_normalizes_string_ports(self):
            """Return string ports unchanged.

            Given: A list of port strings
            When: Calling _normalize_ports(["8080:80", "443:443"])
            Then: Should return the same list as strings
            """
            result = ProjectManager._normalize_ports(["8080:80", "443:443"])
            assert result == ["8080:80", "443:443"], f"Expected port strings but got {result=}"

        def test_normalizes_dict_ports(self):
            """Extract 'target' key from dict-format port specs.

            Given: A list of dict port specs with target key
            When: Calling _normalize_ports([{"target": 80}])
            Then: Should return ["80"]
            """
            result = ProjectManager._normalize_ports([{"target": 80, "published": 8080}])
            assert result == ["80"], f"Expected ['80'] but got {result=}"

    class TestNormalizeEnvironment:
        """Tests for _normalize_environment() static method."""

        def test_returns_empty_dict_for_none(self):
            """Return empty dict for None environment.

            Given: None as raw environment value
            When: Calling _normalize_environment(None)
            Then: Should return {}
            """
            result = ProjectManager._normalize_environment(None)
            assert result == {}, f"Expected {{}} but got {result=}"

        def test_normalizes_dict_environment(self):
            """Return dict environment as-is, stringifying values.

            Given: A dict with string key-value pairs
            When: Calling _normalize_environment({"KEY": "value"})
            Then: Should return the same dict
            """
            result = ProjectManager._normalize_environment({"KEY": "value", "PORT": 8000})
            assert result["KEY"] == "value", f"Expected 'value' but got {result['KEY']=}"
            assert result["PORT"] == "8000", f"Expected '8000' but got {result['PORT']=}"

        def test_normalizes_list_environment(self):
            """Parse KEY=VALUE list format into a dict.

            Given: A list of "KEY=value" strings
            When: Calling _normalize_environment(["KEY=value", "PORT=8000"])
            Then: Should return {"KEY": "value", "PORT": "8000"}
            """
            result = ProjectManager._normalize_environment(["KEY=value", "PORT=8000"])
            assert result == {"KEY": "value", "PORT": "8000"}, f"Expected parsed env but got {result=}"

    class TestLoad:
        """Tests for load()."""

        def test_returns_none_for_missing_directory(self, tmp_path, mocker):
            """Return None when the project directory does not exist.

            Given: A projects_path with no subdirectory matching the project id
            When: Calling load("nonexistent")
            Then: Should return None
            """
            mocker.patch(
                "app.services.project_manager.get_settings",
                return_value=mocker.MagicMock(projects_path=str(tmp_path)),
            )
            manager = ProjectManager()
            result = manager.load("nonexistent")
            assert result is None, f"Expected None but got {result=}"

        def test_returns_none_for_path_traversal(self, tmp_path, mocker):
            """Return None when project id attempts path traversal.

            Given: A project id with path traversal characters
            When: Calling load("../../etc")
            Then: Should return None (not raise)
            """
            mocker.patch(
                "app.services.project_manager.get_settings",
                return_value=mocker.MagicMock(projects_path=str(tmp_path)),
            )
            manager = ProjectManager()
            result = manager.load("../../etc")
            assert result is None, f"Expected None for traversal attempt but got {result=}"

        def test_returns_none_when_no_compose_file(self, tmp_path, mocker):
            """Return None when directory has no docker-compose file.

            Given: A project directory with no supported compose file
            When: Calling load("emptyproject")
            Then: Should return None
            """
            project_dir = tmp_path / "emptyproject"
            project_dir.mkdir()
            mocker.patch(
                "app.services.project_manager.get_settings",
                return_value=mocker.MagicMock(projects_path=str(tmp_path)),
            )
            manager = ProjectManager()
            result = manager.load("emptyproject")
            assert result is None, f"Expected None but got {result=}"

        def test_loads_project_from_compose_file(self, tmp_path, mocker):
            """Return a ProjectModel parsed from a valid docker-compose.yml.

            Given: A project directory with a docker-compose.yml containing one service
            When: Calling load("myproject")
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
            mocker.patch(
                "app.services.project_manager.get_settings",
                return_value=mocker.MagicMock(projects_path=str(tmp_path)),
            )
            manager = ProjectManager()
            result = manager.load("myproject")

            assert result is not None, "Expected ProjectModel but got None"
            assert result.id == "myproject", f"Expected 'myproject' but got {result.id=}"
            assert len(result.services) == 1, f"Expected 1 service but got {len(result.services)=}"
            assert result.services[0].name == "web", f"Expected 'web' but got {result.services[0].name=}"
            assert result.services[0].image == "nginx:alpine", (
                f"Expected 'nginx:alpine' but got {result.services[0].image=}"
            )

    class TestListAll:
        """Tests for list_all()."""

        def test_returns_empty_list_when_projects_path_missing(self, tmp_path, mocker):
            """Return empty list when the projects directory does not exist.

            Given: A projects_path pointing to a non-existent directory
            When: Calling list_all()
            Then: Should return []
            """
            mocker.patch(
                "app.services.project_manager.get_settings",
                return_value=mocker.MagicMock(projects_path=str(tmp_path / "missing")),
            )
            manager = ProjectManager()
            result = manager.list_all()
            assert result == [], f"Expected empty list but got {result=}"

        def test_returns_all_valid_projects(self, tmp_path, mocker):
            """Return only valid projects (those with a compose file).

            Given: Two project directories, only one with a docker-compose.yml
            When: Calling list_all()
            Then: Should return 1 ProjectModel
            """
            proj_a = tmp_path / "project-a"
            proj_a.mkdir()
            (proj_a / "docker-compose.yml").write_text("services:\n  api:\n    image: python:3.12\n")

            proj_b = tmp_path / "project-b"
            proj_b.mkdir()
            # No compose file — should be skipped

            mocker.patch(
                "app.services.project_manager.get_settings",
                return_value=mocker.MagicMock(projects_path=str(tmp_path)),
            )
            manager = ProjectManager()
            result = manager.list_all()

            assert len(result) == 1, f"Expected 1 project but got {len(result)=}"
            assert result[0].id == "project-a", f"Expected 'project-a' but got {result[0].id=}"
>>>>>>> 62afd77 (test(api): add unit tests, fix guidelines violations, update docs\n\n- Single outer test class with nested sub-classes (no multiple module-level classes)\n- No type annotations in test helpers or factory functions\n- No imports inside fixture/method bodies\n- No noqa comments\n- mocker.patch for all mocking, Given-When-Then docstrings\n- conftest: move security import to module level\n- docs: rewrite README, update changelog, fix stale make targets")
