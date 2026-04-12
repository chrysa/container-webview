______________________________________________________________________

## applyTo: "api/\*\*/\*.py"

# Ruff Compliance Guidelines

**Applies to:** `api/**/*.py`

**Version:** 1.0 (adapted from Padam-AV guidelines)

______________________________________________________________________

## Ruff as Source of Truth

Ruff is the single linting authority for this project. It ensures:

- ✅ **Code Quality**: Consistent formatting, import sorting, complexity checks
- ✅ **Security**: Vulnerability detection (S rules)
- ✅ **Type Safety**: Enforcement of type annotations (ANN rules)
- ✅ **Performance**: Anti-pattern detection (PERF rules)
- ✅ **Consistency**: Uniform code style

**Golden Rule:** If Ruff fails locally, it will fail in CI. Fix it before pushing.

______________________________________________________________________

## Priority Rule Categories

### Import Management (I001)

- **Automatic sorting**: Imports sorted by Ruff
- **Group separation**: Standard library → third-party → local; separated by blank lines
- **Type checking imports**: Use `if typing.TYPE_CHECKING:` blocks for type-only imports

### Type Annotations (ANN Series)

- **ANN001**: All function arguments must have type annotations
- **ANN002**: `*args` must have type annotations
- **ANN003**: `**kwargs` must have type annotations
- **ANN201**: Public functions must have return type annotations
- **ANN205**: Static methods must have return type annotations
- **ANN206**: Class methods must have return type annotations

### Argument Management (ARG Series)

- **ARG001-005**: Remove unused arguments (use `_` prefix if required by interface)

### Security (S Series)

- **S105**: No hardcoded password strings
- **S106**: No hardcoded password function arguments
- **S311**: Use `secrets` module for cryptographic randomness
- **S113**: Always set timeout for requests

### Performance (PERF Series)

- **PERF401**: Use list comprehensions instead of manual loops where appropriate

### Code Complexity (PLR Series)

- **PLR0913**: Maximum 10 arguments per function
- **PLR2004**: Avoid magic number comparisons (use named constants)

### Boolean Arguments (FBT Series)

- **FBT001**: Avoid boolean type hints in positional arguments
- **FBT002**: Avoid boolean default values in positional arguments
- Use enums or keyword-only arguments instead

### Exception Handling (BLE/B Series)

- **BLE001**: Don't catch bare `Exception`, be specific
- **B904**: Use `raise ... from ...` for exception chaining **inside `except` blocks**
- **B027**: Abstract methods must use `@abstractmethod` decorator

### Logging (G Series)

- **G004**: Don't use f-strings in logging calls — use `%s` parameterized format
- **G201**: Use `exc_info=True` instead of `logging.exception()`

### Class Design (RUF Series)

- **RUF012**: Mutable class attributes must use `field(default_factory=...)`

______________________________________________________________________

## Common Violation Patterns

### Pattern 1: Logging with f-strings (G004)

```python
# ❌ Bad
_logger.warning(f"Docker unavailable: {exc}")

# ✅ Good
_logger.warning("Docker unavailable: %s", exc)
```

### Pattern 2: Missing type annotations (ANN001/ANN201)

```python
# ❌ Bad
def get_container(project_id, service_name):
    return None

# ✅ Good
def get_container(project_id: str, service_name: str) -> Container | None:
    return None
```

### Pattern 3: Exception handling (BLE001 / B904)

```python
# ❌ Bad — too broad
try:
    risky()
except Exception as exc:
    raise CustomError("Failed")

# ✅ Good
try:
    risky()
except docker.errors.DockerException as exc:
    raise CustomError("Failed to connect to Docker") from exc
```

### Pattern 4: Bare suppress via nested try (use contextlib.suppress)

```python
# ❌ Bad — nested try/except in finally
finally:
    try:
        await websocket.close()
    except RuntimeError:
        pass

# ✅ Good
finally:
    with contextlib.suppress(RuntimeError):
        await websocket.close()
```

### Pattern 5: Magic numbers (PLR2004)

```python
# ❌ Bad
if status_code == 200:
    return data

# ✅ Good — use HTTPStatus or a named constant
from http import HTTPStatus
if status_code == HTTPStatus.OK:
    return data
```

### Pattern 6: Boolean positional arguments (FBT001/FBT002)

```python
# ❌ Bad
def connect(host: str, use_ssl: bool = True) -> None:
    pass

# ✅ Good — use enum or keyword-only
class ConnectionMode(StrEnum):
    SSL = "ssl"
    PLAIN = "plain"

def connect(host: str, *, mode: ConnectionMode = ConnectionMode.SSL) -> None:
    pass
```

### Pattern 7: Unused method arguments (ARG002)

```python
# ❌ Bad — ARG002
def on_event(self, client, obj):
    pass

# ✅ Good — prefix with underscore
def on_event(self, _client, _obj):
    pass
```

______________________________________________________________________

## Ruff CLI Commands

```bash
# Check all files
ruff check api/

# Auto-fix all auto-fixable issues
ruff check api/ --fix

# Format all files (Black-like)
ruff format api/

# Check specific file
ruff check api/app/services/docker_client.py

# Show specific rule details
ruff rule G004
```

______________________________________________________________________

## Development Workflow

1. **Write code** following guidelines
1. **Run Ruff** locally: `ruff check api/ --fix`
1. **Address remaining** violations manually
1. **Commit** when all checks pass

**Zero `# noqa` policy**: Never suppress violations. Fix the root cause always.
