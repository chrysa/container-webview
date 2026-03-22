---
applyTo: "api/**/*.py"
---

# Python Typing Guidelines

**Applies to:** `api/**/*.py`

**Version:** 1.0 (adapted from Padam-AV guidelines)

---

## Project Overview: Type Safety First

100% type annotations are required on all production code. This ensures:

- ✅ **Type Safety**: Catch errors before runtime via static analysis
- ✅ **IDE Support**: Better autocomplete and refactoring
- ✅ **Documentation**: Types serve as inline documentation
- ✅ **Maintainability**: Clear contracts between functions/classes
- ✅ **Compliance**: Ruff rule ANN enforces all public functions have types

**Golden Rule:** No `Any` unless absolutely necessary. Use specific types or `Union` instead.

---

## Rules

### Core Typing Rules

- All functions, methods, and class attributes must have explicit type hints (PEP 484, Python 3.12+)
- Use built-in generics (`list[str]`, `dict[str, int]`, `tuple[str, ...]`) — **never** `List`, `Dict`, `Tuple` from `typing`
- Use `| None` for nullable types — **never** `Optional[T]`
- Use `X | Y` for union types — **never** `Union[X, Y]`
- Prefer precise types over `Any`
- No type comments: always use inline type hints

### `from __future__ import annotations` Usage

- Use `from __future__ import annotations` **ONLY** in files that also contain an `if typing.TYPE_CHECKING:` block
- If a file has no `if typing.TYPE_CHECKING:` block → do **NOT** add `from __future__ import annotations`

```python
# ✅ CORRECT — has TYPE_CHECKING block
from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    from docker.models.containers import Container

def get_container(name: str) -> Container | None: ...

# ✅ CORRECT — no TYPE_CHECKING block, no __future__ needed
from datetime import timedelta

def create_token(expires_delta: timedelta | None = None) -> str: ...

# ❌ WRONG — __future__ without TYPE_CHECKING block
from __future__ import annotations

from datetime import timedelta

def create_token(expires_delta: timedelta | None = None) -> str: ...
```

### `typing.TYPE_CHECKING` Pattern

Use `if typing.TYPE_CHECKING:` to import types that are only needed for annotations — avoids circular imports and runtime overhead:

```python
import typing

if typing.TYPE_CHECKING:
    from docker.models.containers import Container
    from app.services.project_manager import ProjectModel
```

### `Final` Usage

Constants must be typed with `Final`. Import it directly from `typing` inside the `TYPE_CHECKING` block when `from __future__ import annotations` is used, or at module level otherwise:

```python
# In constants.py (has TYPE_CHECKING block)
import typing
from enum import StrEnum

if typing.TYPE_CHECKING:
    from typing import Final

ERR_NOT_FOUND: Final[str] = "Project not found"

# In files without TYPE_CHECKING block — just annotate the constant
_LDAP_DN_TEMPLATE: str = "cn={},{}"
```

---

## Type Annotation Examples

### Function signatures

```python
# ✅ Correct — fully typed
def authenticate(self, username: str, password: str) -> bool:
    ...

def load(self, project_id: str) -> ProjectModel | None:
    ...

def get_all(self) -> list[Alert]:
    ...
```

### Pydantic models

```python
from pydantic import BaseModel

class ServiceModel(BaseModel):
    """Schema for a single service entry in a Compose file."""

    name: str
    image: str | None = None
    ports: list[str] = []
    environment: dict[str, str] = {}
```

### Method with container type from TYPE_CHECKING

```python
from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    from docker.models.containers import Container

def get_container_for_service(
    self, project_id: str, service_name: str
) -> Container | None:
    ...
```

### Avoid `Any`

```python
# ❌ Bad
def parse_stats(self, container: Any, stats: Any) -> ServiceMetrics: ...

# ✅ Good — use dict for unstructured JSON payloads
def _parse_stats(self, container: Container, stats: dict) -> ServiceMetrics: ...
```

---

## Enforcement

- Ruff ANN rules enforce all public functions have type annotations
- Type errors must be fixed before committing
- `# type: ignore` is treated the same as `# noqa` — prohibited; fix the root cause
