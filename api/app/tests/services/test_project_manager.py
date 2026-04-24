import pytest


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
