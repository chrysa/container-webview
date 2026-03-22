---
applyTo: "api/**/*.py"
---

# Python Development Guidelines

**Applies to:** `api/**/*.py`

**Version:** 1.0 (adapted from Padam-AV guidelines)

---

## Project Overview

Docker Overview WebUI backend is built with FastAPI + Python 3.12+, Docker SDK, and JWT authentication. This document establishes mandatory Python development standards.

- ✅ **Code Quality**: Ruff-enforced linting, formatting, and security checks
- ✅ **Maintainability**: PEP 8 compliance, service-class architecture, clear separation of concerns
- ✅ **Type Safety**: 100% type annotations on public APIs
- ✅ **Security**: OWASP Top 10, no hardcoded secrets
- ✅ **Consistency**: Uniform code style across all services

**Golden Rule:** Ruff is the source of truth. If it fails, fix it. No exceptions.

---

## Tech Stack

- **Python**: 3.12+ (required)
- **Framework**: FastAPI with Pydantic v2
- **Auth**: python-jose (JWT), OAuth2PasswordBearer
- **Docker**: docker-py SDK
- **Type Checking**: Ruff ANN rules
- **Linting/Formatting**: Ruff

---

## File and Module Organization

### Import Guidelines

- **Location**: All imports at the top of the file, never inside functions/methods
- **Organization**: Must be sorted and grouped (Ruff I001):
  1. Standard library imports
  2. Third-party library imports
  3. Internal/local imports
- **Separation**: Separate each group with a blank line
- **Future imports**: Use `from __future__ import annotations` **only** in files that contain `if typing.TYPE_CHECKING:` blocks
- **No unused imports**: Each import must be used (F401)
- **No relative imports**: Use absolute imports only
- **Type checking imports**: Use `if typing.TYPE_CHECKING:` for type-only imports

### File Structure

- **One class per file** is preferred; keep files focused
- **Module naming**: Use descriptive, lowercase names with underscores
- **No nested classes/functions**: Avoid nesting except for closures

---

## Code Style and Structure

### Function and Method Design

- **Single return point**: Use a variable to store the result; return **once at the end** (RET)
- **`return None` and bare `return` are PROHIBITED**: Never write `return None` or `return` without a value. Always return via a result variable.
- **Function length**: Keep functions focused and concise (typically < 20 lines)
- **Parameter naming**: Use descriptive names that clearly indicate purpose
- **Argument limits**: Maximum 10 arguments per function (PLR0913)
- **Boolean parameters**: Avoid boolean positional arguments (FBT001/FBT002)
- **Type annotations**: All public functions must have complete type hints (ANN)

#### Single Return Point — Canonical Patterns

**Pattern A — Nullable result (`-> T | None`)**:
```python
# ❌ PROHIBITED — multiple returns, return None
def load(self, project_id: str) -> ProjectModel | None:
    if invalid:
        return None          # ← FORBIDDEN
    if not found:
        return None          # ← FORBIDDEN
    return ProjectModel(...)

# ✅ CORRECT — result variable, single return
def load(self, project_id: str) -> ProjectModel | None:
    project_model: ProjectModel | None = None
    if not invalid and found:
        project_model = ProjectModel(...)
    return project_model
```

**Pattern B — `-> None` functions (no early exit)**:
```python
# ❌ PROHIBITED — bare return
async def stream_logs(self, websocket: WebSocket) -> None:
    if not authorized:
        await websocket.close(code=4001)
        return                           # ← FORBIDDEN
    await websocket.accept()

# ✅ CORRECT — try/except/else + if/else nesting, no return
async def stream_logs(self, websocket: WebSocket) -> None:
    try:
        self._check_auth()
    except HTTPException:
        await websocket.close(code=4001)
    else:
        if not self._project_exists():
            await websocket.close(code=4004)
        else:
            await websocket.accept()
            await self._pipe_logs(websocket)
```

**Pattern C — List accumulator**:
```python
# ❌ PROHIBITED — early return []
def list_all(self) -> list[ProjectModel]:
    if not base.exists():
        return []             # ← FORBIDDEN
    ...

# ✅ CORRECT — empty list initialised, guard as if-branch
def list_all(self) -> list[ProjectModel]:
    projects: list[ProjectModel] = []
    if base.exists():
        for entry in sorted(base.iterdir()):
            ...
    return projects
```

### Control Flow

- **Mapping over cascading**: Prefer dictionaries to cascades of if/elif for dispatch
- **No early returns for None/empty**: See single return point patterns above
- **Exception handling**: Handle specific exceptions, avoid bare `except:` (BLE001)
- **Raise from**: Use `raise ... from ...` for exception chaining (B904)
- **Security**: No hardcoded passwords or secrets (S105, S106)
- **Logging**: Use parameterized logging, not f-strings (G004)
- **contextlib.suppress**: Use instead of `try/except: pass` for intentionally suppressed exceptions

### Ruff Compliance — Zero `# noqa` Policy

- **`# noqa` comments are strictly prohibited**: Never suppress Ruff violations inline.
- **Fix the root cause**: Every Ruff violation must be resolved by correcting the code.
- **Rationale**: Suppressing violations hides design problems.

### Variable and Naming

- **Explicit variable names**: Every variable name must unambiguously convey its content and role
  - No single-letter names (except `i`, `j` loop counters)
  - No abbreviations (`e`, `obj`, `val`, `res`, `tmp`, `msg`)
  - No vague names (`data`, `info`, `result` when a more precise name is possible)
- **Descriptive names**: Use explicit, descriptive English names
- **PEP 8 compliance**: `snake_case` for variables/functions, `PascalCase` for classes
- **Constants**: Use `UPPER_CASE` for module-level constants
- **Private members**: Use leading underscore for internal class properties/methods

---

## Constants and Enums

### Enum Usage Requirements

- **StrEnum for string constants**: Use `StrEnum` for all string-based constants
- **IntEnum for integer constants**: Use `IntEnum` for all integer-based constants
- **Descriptive enum names**: PascalCase class names (e.g., `ContainerState`, `AlertLevel`)
- **Descriptive member names**: UPPER_CASE members (e.g., `RUNNING`, `CRITICAL`)

### File Structure Standards

```python
from __future__ import annotations

import typing
from enum import StrEnum

if typing.TYPE_CHECKING:
    from typing import Final

# =============================================================================
# ENUMS
# =============================================================================

class ContainerState(StrEnum):
    """Container lifecycle states as returned by the Docker SDK."""

    RUNNING = "running"
    EXITED = "exited"
    RESTARTING = "restarting"
    UNKNOWN = "unknown"

# =============================================================================
# CONSTANTS - Static values
# =============================================================================

ERR_PROJECT_NOT_FOUND: Final[str] = "Project not found"
ERR_UNKNOWN_ACTION: Final[str] = "Unknown action: {}"
```

---

## Code Quality Requirements

### Documentation

- **Docstrings**: All public functions, classes, and methods must have docstrings
- **Style**: Google or reStructuredText style docstrings
- **Coverage**: Document parameters, return values, and exceptions
- **Language**: English for code; French allowed in comments and docstrings

### Type Hints

- **Comprehensive typing**: Type hints required for all function signatures
- **Built-in types**: Use built-in types (`list[str]`) over typing module when possible
- **Union types**: Use `| None` instead of `Optional`
- **TYPE_CHECKING**: Import typing-only modules within `if typing.TYPE_CHECKING:` blocks

### Error Handling

- **Specific exceptions**: Catch and raise specific exception types
- **Error messages**: Provide clear, actionable error messages
- **Logging**: Use the `logging` module (`_logger = logging.getLogger(__name__)`), never `print()`
- **Fail fast**: Validate inputs early
- **No HTTP coupling in services**: Services raise `ValueError`; routers translate to `HTTPException`

---

## Architecture and Design Patterns

### Service Layer

- **Business logic**: Place business logic in service classes (`services/`)
- **Thin routers**: Keep FastAPI routes lightweight, delegate to services
- **No HTTP imports in services**: Services must not import `HTTPException` or anything from `fastapi`
- **Services raise ValueError**: Routers catch `ValueError` and translate to `HTTPException`

### Class Design

- **Single responsibility**: Each class should have one clear responsibility
- **Composition over inheritance**: Prefer composition when possible
- **Alphabetical ordering**: Sort methods/properties alphabetically within classes
- **Property organization**: Properties > staticmethod > classmethod > methods

### Security Considerations

- **No hardcoded secrets**: Use `pydantic-settings` + `.env` file
- **Input validation**: Validate and sanitize all user inputs
- **Path traversal**: Use `pathlib.Path.resolve()` and verify path stays within base directory
- **Authentication**: JWT via `python-jose`, `SecurityService` class

---

## Performance Guidelines

- **List comprehensions**: Use when appropriate for readability and performance
- **Generator expressions**: Use for memory-efficient iteration
- **Built-in functions**: Leverage Python built-ins

---

## Build System (`pyproject.toml`)

Always use `setuptools.build_meta` as the build backend. **Never** use `setuptools.backends.legacy:build` — that path was experimental and was removed in later setuptools releases, causing `BackendUnavailable` errors inside Docker.

```toml
# ✅ CORRECT
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

# ❌ BROKEN — BackendUnavailable: Cannot import 'setuptools.backends.legacy'
[build-system]
requires = ["setuptools>=70", "wheel"]
build-backend = "setuptools.backends.legacy:build"
```

---

## Development Workflow

### Local Development Restrictions

- **NO local Python execution**: Never run Python commands on local machine
- **Container-based**: All Python execution must be within Docker containers
- **Make targets**: Use `Makefile` targets for all development tasks

### Language and Comments

- **Code language**: All code, variables, functions in English
- **Comments in French**: Comments and docstrings may be in French for team clarity
- **Error messages**: User-facing messages in English

---

## Enforcement

- CI/CD integration checks all rules
- Code quality violations block merges
- `# noqa` is rejected in code review
