# Docker Overview WebUI — Testing Instructions

---
description: "Comprehensive testing guidelines for the Docker Overview WebUI project. STRICT: All user requirements are MANDATORY. Mock ALL external dependencies (Docker SDK, filesystem) in unit tests. Strict compliance: assertions, fixture patterns, no typing in tests, Given-When-Then docstrings."
applyTo: "api/**/tests/**/*.py"
---

> **⚠️ IMPORTANT**: This file is an **additional layer** on top of [`python_guidelines.instructions.md`](./python_guidelines.instructions.md). All general Python rules apply to test code; conflicts favor this file for test-specific rules.

---

## Tech Stack for Testing

- **pytest**: Main test runner with `pytest-mock`, `pytest-asyncio`
- **pytest-mock**: `mocker` fixture for patching and mocking (preferred over `unittest.mock`)
- **httpx + pytest-asyncio**: Async HTTP client testing for FastAPI endpoints
- **faker**: Generate realistic test data with `faker` fixture
- **coverage.py**: Generate coverage reports; target 100% for core logic

### Project Configuration

```toml
# pyproject.toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["api/app/tests"]

[tool.coverage.run]
source = ["api/app"]
omit = ["*/tests/*"]
```

### Make Commands

```bash
make tests            # Run all tests
make tests-cov        # Run with coverage report
make tests-html       # Run with HTML coverage report
```

---

## MANDATORY REQUIREMENTS

- **MANDATORY**: Mock ALL Docker SDK calls in unit tests (`mocker.patch()`)
- **MANDATORY**: Mock ALL external dependencies (filesystem, network, Docker daemon)
- **MANDATORY**: Integration tests are the ONLY ones allowed to use a real Docker socket (marked `@pytest.mark.integration`)
- **MANDATORY**: Every `assert` statement MUST include a descriptive error message (f-string debug `{variable=}`)
- **MANDATORY**: No typing in tests, fixtures (no annotations, no TYPE_CHECKING blocks)
- **MANDATORY**: All test methods MUST have Given-When-Then docstrings
- **MANDATORY**: Fixtures MUST follow `_load(**kwargs)` parameterizable pattern
- **MANDATORY**: Fixture function names MUST start with `fixt_` prefix; decorator MUST have `name="..."` attribute
- **MANDATORY**: Prefer `@pytest.mark.parametrize` over loops in tests
- **MANDATORY**: English only (code, names, comments)

**ANY deviation from these rules must be corrected immediately.**

---

## Critical Rules

### 1. Assertion Messages (CRITICAL)

Every `assert` MUST have a descriptive message using f-string debug format `{variable=}`.

```python
# PROHIBITED
assert result.status_code == 200
assert container.name == "my_container"

# MANDATORY
assert result.status_code == 200, f"Expected 200 but got {result.status_code=}"
assert container.name == "my_container", f"Unexpected container name: {container.name=}"
```

### 2. Mocking in Unit Tests (CRITICAL)

Mock ALL Docker SDK calls, filesystem access, and external dependencies in unit tests.

```python
# PROHIBITED — Real Docker daemon access in service test
def test_get_containers(self):
    service = DockerClientService()
    containers = service.get_all_containers()  # Real Docker call!
    assert len(containers) >= 0

# MANDATORY — Mock Docker client
def test_get_containers(self, mocker):
    """Get all containers with mocked Docker client.

    Given: Docker client service with mocked SDK
    When: Calling get_all_containers()
    Then: Should return list of containers from mock
    """
    mock_containers = [mocker.MagicMock(name="container_1")]
    mock_client = mocker.patch("app.services.docker_client.DockerClientService._client")
    mock_client.containers.list.return_value = mock_containers

    service = DockerClientService()
    result = service.get_all_containers()

    assert result == mock_containers, f"Expected {mock_containers=} but got {result=}"
    mock_client.containers.list.assert_called_once()
```

**Test Classification:**

| Test Type | Mock Required? | Marker | Real Docker? |
|---|---|---|---|
| **Services** | ✅ YES | ❌ none | ❌ NO |
| **Routers** | ✅ YES (mock services) | ❌ none | ❌ NO |
| **Docker integration** | ❌ NO | ✅ `@pytest.mark.integration` | ✅ YES |

### 3. No Typing in Tests (MANDATORY)

```python
# PROHIBITED
def test_service(docker_service: DockerClientService) -> None:
    pass

# MANDATORY
def test_service(docker_service):
    pass
```

### 4. Given-When-Then Docstrings (MANDATORY)

All test methods must have a Given-When-Then docstring. Do NOT add docstrings to fixtures or factory functions.

```python
def test_get_project_containers(self, mocker):
    """Get containers filtered by project label.

    Given: Docker client returning 3 containers, 2 with matching project label
    When: Calling get_containers_for_project("my_project")
    Then: Should return only the 2 matching containers
    """
    # implementation
```

---

## Test Class Structure (MANDATORY)

Use a **single main test class** with **nested sub-classes** for logical grouping. Never create multiple test classes at module level for the same service.

```python
# ✅ CORRECT — Single main class with nested sub-classes
class TestDockerClientService:
    """Unit tests for DockerClientService."""

    class TestContainerList:
        """Tests for container listing operations."""

        def test_list_all_containers(self, mocker):
            """List all running containers.

            Given: Docker client with 2 running containers
            When: Calling get_all_containers()
            Then: Should return list of 2 containers
            """
            pass

        def test_list_containers_empty(self, mocker):
            """List containers when none are running.

            Given: Docker daemon with no running containers
            When: Calling get_all_containers()
            Then: Should return empty list
            """
            pass

    class TestContainerLookup:
        """Tests for individual container lookup."""

        def test_get_container_by_id(self, mocker):
            """Look up a container by its ID.

            Given: A specific container ID exists in Docker
            When: Calling get_container("abc123")
            Then: Should return the matching container
            """
            pass


# ❌ INCORRECT — Multiple module-level classes
class TestDockerClientServiceList:
    pass

class TestDockerClientServiceLookup:  # WRONG — split at module level
    pass
```

---

## Fixture Patterns (MANDATORY)

All fixtures must use the `_load(**kwargs)` parameterizable pattern with sensible faker-based defaults.

```python
# PROHIBITED — Static fixture
@pytest.fixture(name="project_data")
def fixt_project_data():
    return {"name": "my_project"}  # Hardcoded value

# PROHIBITED — Missing fixt_ prefix
@pytest.fixture(name="project_data")
def project_data(faker):  # WRONG: should be fixt_project_data
    pass

# PROHIBITED — Missing name attribute
@pytest.fixture
def fixt_project_data(faker):  # WRONG: should have name="project_data"
    pass

# MANDATORY — Correct pattern
@pytest.fixture(name="project_data")
def fixt_project_data(faker):
    def _load(**kwargs):
        return {
            "name": kwargs.get("name", faker.slug()),
            "path": kwargs.get("path", f"/projects/{faker.slug()}"),
        }
    return _load


@pytest.fixture(name="container_mock")
def fixt_container_mock(mocker):
    def _load(**kwargs):
        mock = mocker.MagicMock()
        mock.id = kwargs.get("id", "abc123def456")
        mock.name = kwargs.get("name", "project_service_1")
        mock.status = kwargs.get("status", "running")
        mock.labels = kwargs.get("labels", {"com.docker.compose.project": "myproject"})
        return mock
    return _load
```

### Fixture Scope Rules

- **DEFAULT**: `scope="function"` (omit scope parameter)
- **OPTIMIZE**: Use wider scope only when data is immutable and never modified by tests
- **REQUIRED** function scope: when fixture creates Docker mock objects, uses `mocker`

---

## Integration Tests (Docker)

Integration tests require a real Docker daemon. Mark them explicitly.

```python
# Integration test — requires real Docker socket
@pytest.mark.integration
class TestDockerClientIntegration:
    """Integration tests with real Docker daemon."""

    def test_list_containers_real(self):
        """Test listing containers against real Docker daemon.

        Given: Real Docker daemon running
        When: Calling get_all_containers()
        Then: Should return list without errors
        """
        service = DockerClientService()
        result = service.get_all_containers()

        assert isinstance(result, list), f"Expected list but got {type(result)=}"
```

---

## Router Testing with FastAPI TestClient

Use `httpx.AsyncClient` with FastAPI `app` for router tests. Mock the service layer entirely.

```python
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


class TestProjectsRouter:
    """Unit tests for /projects router."""

    class TestListProjects:
        """Tests for GET /projects endpoint."""

        async def test_list_projects_success(self, mocker):
            """List projects successfully.

            Given: ProjectManager returning 2 projects
            When: GET /projects
            Then: Should return 200 with project list
            """
            mock_projects = [{"name": "proj1"}, {"name": "proj2"}]
            mocker.patch(
                "app.routers.projects.get_project_manager",
                return_value=mocker.MagicMock(list_projects=lambda: mock_projects),
            )

            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.get("/projects")

            assert response.status_code == 200, f"Expected 200 but got {response.status_code=}"
            data = response.json()
            assert len(data) == 2, f"Expected 2 projects but got {len(data)=}"

        async def test_list_projects_unauthorized(self):
            """Reject unauthenticated request.

            Given: No Authorization header
            When: GET /projects
            Then: Should return 401
            """
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.get("/projects")

            assert response.status_code == 401, f"Expected 401 but got {response.status_code=}"
```

---

## Parametrized Tests (PREFERRED over loops)

```python
# PROHIBITED — Loop in test
def test_container_states(self, mocker):
    for state in ["running", "stopped", "paused"]:
        # test logic repeated
        pass

# MANDATORY — @pytest.mark.parametrize
@pytest.mark.parametrize("state,expected_active", [
    ("running", True),
    ("stopped", False),
    ("paused", False),
])
def test_container_state_active(self, state, expected_active, mocker):
    """Check container active state per Docker status.

    Given: Container with given Docker state
    When: Checking is_active property
    Then: Should match expected boolean
    """
    mock_container = mocker.MagicMock()
    mock_container.status = state

    result = is_container_active(mock_container)

    assert result == expected_active, f"For {state=} expected {expected_active=} but got {result=}"
```

---

## File Structure

```
api/app/tests/
├── conftest.py                     # Shared fixtures and pytest config
├── test_main.py                    # Health check / ping tests
├── services/
│   ├── test_docker_client.py       # DockerClientService unit tests
│   ├── test_project_manager.py     # ProjectManager unit tests
│   ├── test_auth_service.py        # AuthService unit tests
│   ├── test_lifecycle_service.py   # LifecycleService unit tests
│   ├── test_metrics_service.py     # MetricsService unit tests
│   ├── test_alerts_service.py      # AlertsService unit tests
│   └── test_topology_service.py    # TopologyService unit tests
└── routers/
    ├── test_projects.py            # /projects router tests
    ├── test_lifecycle.py           # /lifecycle router tests
    ├── test_metrics.py             # /metrics router tests
    ├── test_alerts.py              # /alerts router tests
    ├── test_topology.py            # /topology router tests
    └── test_auth.py                # /auth router tests
```
