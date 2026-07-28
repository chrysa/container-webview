# Incident Correlation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an intelligence layer that fuses Docker events, log error bursts, and metric anomalies into dated incidents with a probable cause and a fused timeline, surfaced host-wide and filterable by project.

**Architecture:** A host-wide collector (asyncio tasks in the FastAPI lifespan) writes Docker events and metric samples into Postgres + TimescaleDB. A correlation service turns triggers into incidents (deterministic cause + optional Ollama narrative). New REST + WebSocket routes serve an `/incidents` React page. The repo adopts the chrysa DB stack (SQLAlchemy 2.0 async + Alembic) it did not previously use.

**Tech Stack:** FastAPI, docker-py 7.1, SQLAlchemy 2.0 async, asyncpg, Alembic, Postgres 16 + TimescaleDB, Pydantic Settings, pytest + testcontainers, React 19 + Vite 8 + TS, TanStack Query v5, ReactFlow, Recharts, Vitest, Playwright.

## Global Constraints

- Language: **English** for all code, comments, docs, config.
- Commits: **Conventional Commits** (`feat`, `fix`, `chore`, `docs`, `refactor`, `test`, `ci`).
- **No hardcoded constants** — all thresholds/intervals in external YAML, read via a typed Pydantic Settings loader. Only language-level enums (e.g. `status.HTTP_*`) exempt.
- **DDD**: domain logic in `api/app/services/`; routers only delegate.
- **Strict typing**: mypy clean, no `any` in TypeScript.
- Semantic REST URLs: plural-noun collections, no verbs in paths; follow the `api-design` skill; RFC-7807 errors.
- All incident routes require `Depends(get_current_user)`; WebSocket auth via `?token=` query param (same as `routers/logs.py`).
- **Dark mode** mandatory; **WCAG 2.1 AA**.
- Coverage target **≥ 85%** (raise `fail_under` from 78 progressively; final gate 85).
- Max function 50 lines · max file 500 lines · cyclomatic complexity ≤ 10.
- Network: TanStack Query for all HTTP; no direct `fetch` in components.
- Config keys (external YAML): `COLLECTOR_STATS_INTERVAL_S=10`, `INCIDENT_WINDOW_S=90`, `INCIDENT_RESOLVE_S=120`, `METRIC_RETENTION_DAYS=7`, `ANOMALY_Z_THRESHOLD=3.0`, `ANOMALY_MIN_SUSTAIN_S=15`, `LOG_BURST_RATE=10`, `LOG_BURST_WINDOW_S=30`, `OLLAMA_ENABLED=false`, `OLLAMA_MODEL=llama3.2:3b`, `OLLAMA_URL=http://localhost:11434`.

---

## File Structure

**Backend (`api/app/`)**
- `db/__init__.py`, `db/session.py` — async engine + session factory.
- `db/base.py` — declarative base.
- `models/metric_sample.py`, `models/docker_event.py`, `models/incident.py`, `models/incident_signal.py`, `models/log_excerpt.py` — one model per file.
- `config/intelligence.yaml` + loader fields in `config.py` — external constants.
- `collector/__init__.py`, `collector/event_consumer.py`, `collector/stats_poller.py`, `collector/log_tailer.py`, `collector/supervisor.py` — collection.
- `services/anomaly_service.py` — EWMA / z-score detector.
- `services/incidents_service.py` — trigger → window → group → cause → narrative.
- `services/narrative_service.py` — Ollama client + template fallback.
- `services/cause_rules.py` — ordered deterministic rules.
- `routers/incidents.py` — REST + WS.
- `schemas/incident.py` — Pydantic response schemas.
- `alembic/` — migration env + versions.

**Frontend (`code/src/`)**
- `domain/incidents/types.ts`, `domain/incidents/queries.ts` — types + TanStack hooks.
- `features/incidents/IncidentsFeed.tsx`, `features/incidents/IncidentDetail.tsx`, `features/incidents/IncidentTimeline.tsx`, `features/incidents/CauseBanner.tsx` — components.
- `pages/Incidents.tsx` — route page.
- `App.tsx` — add lazy route.
- `styles/` — SCSS module per component.

---

## Task 1: DB foundation — async engine + session

**Files:**
- Create: `api/app/db/__init__.py`, `api/app/db/base.py`, `api/app/db/session.py`
- Modify: `api/pyproject.toml` (add deps), `api/app/config.py` (add `database_url`)
- Test: `api/app/tests/db/test_session.py`

**Interfaces:**
- Produces: `get_session() -> AsyncIterator[AsyncSession]` (FastAPI dependency), `engine`, `AsyncSessionLocal`, `Base` (declarative base).

- [ ] **Step 1: Add dependencies**

Edit `api/pyproject.toml` `dependencies`: add
```toml
"sqlalchemy[asyncio]>=2.0.36",
"asyncpg>=0.30",
"alembic>=1.14",
```
Add to dev/test deps:
```toml
"testcontainers[postgres]>=4.8",
```

- [ ] **Step 2: Add config field**

In `api/app/config.py` `Settings`, add:
```python
database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/overview"
```

- [ ] **Step 3: Write the declarative base**

`api/app/db/base.py`:
```python
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""
```

- [ ] **Step 4: Write the session module**

`api/app/db/session.py`:
```python
from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import get_settings

_settings = get_settings()
engine = create_async_engine(_settings.database_url, pool_pre_ping=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with AsyncSessionLocal() as session:
        yield session
```
`api/app/db/__init__.py`:
```python
from app.db.base import Base
from app.db.session import AsyncSessionLocal, engine, get_session

__all__ = ["Base", "AsyncSessionLocal", "engine", "get_session"]
```

- [ ] **Step 5: Write the failing test**

`api/app/tests/db/test_session.py`:
```python
import pytest
from sqlalchemy import text
from testcontainers.postgres import PostgresContainer

from app.db.base import Base


@pytest.mark.asyncio
async def test_session_executes_select_one():
    with PostgresContainer("postgres:16") as pg:
        url = pg.get_connection_url().replace("psycopg2", "asyncpg")
        from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

        engine = create_async_engine(url)
        async with async_sessionmaker(engine)() as session:
            result = await session.execute(text("SELECT 1"))
            assert result.scalar_one() == 1
        await engine.dispose()


def test_base_is_declarative():
    assert hasattr(Base, "metadata")
```

- [ ] **Step 6: Run test to verify it passes**

Run: `cd api && make docker-test` (or `pytest app/tests/db/test_session.py -v`)
Expected: PASS (Postgres 16 container spins up, `SELECT 1` returns 1).

- [ ] **Step 7: Commit**

```bash
git add api/app/db api/app/config.py api/pyproject.toml api/app/tests/db
git commit -m "feat(db): add async SQLAlchemy engine, session, and declarative base"
```

---

## Task 2: ORM models + Alembic + TimescaleDB hypertable

**Files:**
- Create: `api/app/models/metric_sample.py`, `docker_event.py`, `incident.py`, `incident_signal.py`, `log_excerpt.py`, `api/app/models/__init__.py`
- Create: `api/alembic.ini`, `api/alembic/env.py`, `api/alembic/versions/0001_initial.py`
- Test: `api/app/tests/models/test_schema.py`

**Interfaces:**
- Consumes: `Base` from Task 1.
- Produces: models `MetricSample`, `DockerEvent`, `Incident`, `IncidentSignal`, `LogExcerpt`; enums `IncidentStatus`, `CauseCategory`, `SignalType`, `NarrativeSource`.

- [ ] **Step 1: Write the enums + models**

`api/app/models/incident.py`:
```python
import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class IncidentStatus(enum.StrEnum):
    OPEN = "open"
    RESOLVED = "resolved"


class CauseCategory(enum.StrEnum):
    MEMORY = "memory"
    CRASH = "crash"
    READINESS = "readiness"
    CASCADE = "cascade"
    RESOURCE = "resource"
    UNDETERMINED = "undetermined"


class NarrativeSource(enum.StrEnum):
    OLLAMA = "ollama"
    TEMPLATE = "template"


class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[int] = mapped_column(primary_key=True)
    opened_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    container_id: Mapped[str] = mapped_column(String(64), index=True)
    service: Mapped[str] = mapped_column(String(255))
    project: Mapped[str] = mapped_column(String(255), index=True)
    status: Mapped[IncidentStatus] = mapped_column(Enum(IncidentStatus))
    severity: Mapped[str] = mapped_column(String(16))
    cause_category: Mapped[CauseCategory] = mapped_column(Enum(CauseCategory))
    narrative: Mapped[str] = mapped_column(String(2000), default="")
    narrative_source: Mapped[NarrativeSource] = mapped_column(Enum(NarrativeSource))
```

`api/app/models/metric_sample.py`:
```python
from datetime import datetime

from sqlalchemy import DateTime, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class MetricSample(Base):
    __tablename__ = "metric_samples"

    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), primary_key=True)
    container_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    cpu_pct: Mapped[float] = mapped_column(Float)
    mem_pct: Mapped[float] = mapped_column(Float)
    net_rx: Mapped[float] = mapped_column(Float)
    net_tx: Mapped[float] = mapped_column(Float)
    blk_r: Mapped[float] = mapped_column(Float)
    blk_w: Mapped[float] = mapped_column(Float)
```

`api/app/models/docker_event.py`:
```python
import enum
from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DockerEventType(enum.StrEnum):
    DIE = "die"
    OOM = "oom"
    KILL = "kill"
    HEALTH_STATUS = "health_status"
    RESTART = "restart"
    START = "start"
    STOP = "stop"


class DockerEvent(Base):
    __tablename__ = "docker_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    container_id: Mapped[str] = mapped_column(String(64), index=True)
    service: Mapped[str] = mapped_column(String(255), default="")
    project: Mapped[str] = mapped_column(String(255), default="")
    type: Mapped[DockerEventType] = mapped_column(String(32))
    exit_code: Mapped[int | None] = mapped_column(Integer)
    health: Mapped[str | None] = mapped_column(String(32))
```

`api/app/models/incident_signal.py`:
```python
import enum
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class SignalType(enum.StrEnum):
    EVENT = "event"
    METRIC = "metric"
    LOG = "log"


class IncidentSignal(Base):
    __tablename__ = "incident_signals"

    id: Mapped[int] = mapped_column(primary_key=True)
    incident_id: Mapped[int] = mapped_column(ForeignKey("incidents.id"), index=True)
    signal_type: Mapped[SignalType] = mapped_column(String(16))
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    summary: Mapped[str] = mapped_column(String(500))
```

`api/app/models/log_excerpt.py`:
```python
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class LogExcerpt(Base):
    __tablename__ = "log_excerpts"

    id: Mapped[int] = mapped_column(primary_key=True)
    incident_id: Mapped[int] = mapped_column(ForeignKey("incidents.id"), index=True)
    container_id: Mapped[str] = mapped_column(String(64))
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    content: Mapped[str] = mapped_column(Text)
```

`api/app/models/__init__.py`:
```python
from app.models.docker_event import DockerEvent, DockerEventType
from app.models.incident import (
    CauseCategory,
    Incident,
    IncidentStatus,
    NarrativeSource,
)
from app.models.incident_signal import IncidentSignal, SignalType
from app.models.log_excerpt import LogExcerpt
from app.models.metric_sample import MetricSample

__all__ = [
    "DockerEvent", "DockerEventType", "Incident", "IncidentStatus",
    "CauseCategory", "NarrativeSource", "IncidentSignal", "SignalType",
    "LogExcerpt", "MetricSample",
]
```

- [ ] **Step 2: Initialise Alembic**

Run: `cd api && alembic init alembic`
Edit `api/alembic/env.py`: import `from app.db.base import Base` and `import app.models`, set `target_metadata = Base.metadata`, and read the URL from `app.config.get_settings().database_url` (sync driver for migrations: replace `+asyncpg` with `+psycopg` or run via `run_sync`).

- [ ] **Step 3: Write the initial migration**

`api/alembic/versions/0001_initial.py` — `op.create_table(...)` for all five tables (mirror the model columns above), then convert `metric_samples` to a hypertable and set retention:
```python
def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS timescaledb")
    # ... op.create_table for incidents, docker_events, metric_samples,
    #     incident_signals, log_excerpts (columns per models) ...
    op.execute(
        "SELECT create_hypertable('metric_samples', 'ts', if_not_exists => TRUE)"
    )
    op.execute(
        "SELECT add_retention_policy('metric_samples', INTERVAL '7 days')"
    )
```
Guard: if the `timescaledb` extension is unavailable, `CREATE EXTENSION` raises — this is the intended fail-fast (spec §7).

- [ ] **Step 4: Write the failing test**

`api/app/tests/models/test_schema.py`:
```python
import pytest
from sqlalchemy import inspect, text
from testcontainers.postgres import PostgresContainer

from app.db.base import Base
from app.models import Incident  # noqa: F401 ensures models are imported


@pytest.mark.asyncio
async def test_all_tables_created():
    with PostgresContainer("timescale/timescaledb:latest-pg16") as pg:
        url = pg.get_connection_url().replace("psycopg2", "asyncpg")
        from sqlalchemy.ext.asyncio import create_async_engine

        engine = create_async_engine(url)
        async with engine.begin() as conn:
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS timescaledb"))
            await conn.run_sync(Base.metadata.create_all)
            tables = await conn.run_sync(
                lambda c: inspect(c).get_table_names()
            )
        await engine.dispose()
    for name in (
        "incidents", "docker_events", "metric_samples",
        "incident_signals", "log_excerpts",
    ):
        assert name in tables
```

- [ ] **Step 5: Run test to verify it passes**

Run: `cd api && pytest app/tests/models/test_schema.py -v`
Expected: PASS (all five tables present on a Timescale pg16 container).

- [ ] **Step 6: Commit**

```bash
git add api/app/models api/alembic api/alembic.ini api/app/tests/models
git commit -m "feat(models): add incident, event, metric, signal, log ORM models + Timescale migration"
```

---

## Task 3: Intelligence config (external YAML + typed loader)

**Files:**
- Create: `api/app/config/intelligence.yaml`
- Modify: `api/app/config.py` (add `IntelligenceSettings`, loader)
- Test: `api/app/tests/test_intelligence_config.py`

**Interfaces:**
- Produces: `get_intelligence_settings() -> IntelligenceSettings` with fields matching the Global Constraints config keys.

- [ ] **Step 1: Write the YAML**

`api/app/config/intelligence.yaml`:
```yaml
collector_stats_interval_s: 10
incident_window_s: 90
incident_resolve_s: 120
metric_retention_days: 7
anomaly_z_threshold: 3.0
anomaly_min_sustain_s: 15
log_burst_rate: 10
log_burst_window_s: 30
ollama_enabled: false
ollama_model: "llama3.2:3b"
ollama_url: "http://localhost:11434"
```

- [ ] **Step 2: Write the failing test**

`api/app/tests/test_intelligence_config.py`:
```python
from app.config import get_intelligence_settings


def test_intelligence_defaults_loaded_from_yaml():
    s = get_intelligence_settings()
    assert s.collector_stats_interval_s == 10
    assert s.incident_window_s == 90
    assert s.anomaly_z_threshold == 3.0
    assert s.ollama_enabled is False
    assert s.ollama_model == "llama3.2:3b"
```

- [ ] **Step 3: Run test to verify it fails**

Run: `cd api && pytest app/tests/test_intelligence_config.py -v`
Expected: FAIL — `ImportError: cannot import name 'get_intelligence_settings'`.

- [ ] **Step 4: Implement the loader**

In `api/app/config.py`:
```python
from functools import lru_cache
from pathlib import Path

import yaml
from pydantic import BaseModel

_INTELLIGENCE_YAML = Path(__file__).parent / "config" / "intelligence.yaml"


class IntelligenceSettings(BaseModel):
    collector_stats_interval_s: int
    incident_window_s: int
    incident_resolve_s: int
    metric_retention_days: int
    anomaly_z_threshold: float
    anomaly_min_sustain_s: int
    log_burst_rate: int
    log_burst_window_s: int
    ollama_enabled: bool
    ollama_model: str
    ollama_url: str


@lru_cache
def get_intelligence_settings() -> IntelligenceSettings:
    data = yaml.safe_load(_INTELLIGENCE_YAML.read_text(encoding="utf-8"))
    return IntelligenceSettings(**data)
```

- [ ] **Step 5: Run test to verify it passes**

Run: `cd api && pytest app/tests/test_intelligence_config.py -v`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add api/app/config.py api/app/config/intelligence.yaml api/app/tests/test_intelligence_config.py
git commit -m "feat(config): add external intelligence config with typed loader"
```

---

## Task 4: Anomaly detector (EWMA / z-score)

**Files:**
- Create: `api/app/services/anomaly_service.py`
- Test: `api/app/tests/services/test_anomaly_service.py`

**Interfaces:**
- Consumes: `get_intelligence_settings()`.
- Produces: `detect_anomaly(samples: list[float]) -> bool` and `zscore(samples: list[float], value: float) -> float`. `detect_anomaly` returns True when the latest value's z-score exceeds `anomaly_z_threshold`.

- [ ] **Step 1: Write the failing test**

`api/app/tests/services/test_anomaly_service.py`:
```python
from app.services.anomaly_service import detect_anomaly, zscore


def test_zscore_flat_series_is_zero():
    assert zscore([50.0, 50.0, 50.0], 50.0) == 0.0


def test_detect_anomaly_true_on_spike():
    baseline = [60.0] * 20
    assert detect_anomaly([*baseline, 95.0]) is True


def test_detect_anomaly_false_on_stable():
    assert detect_anomaly([61.0, 60.0, 59.0, 60.0, 61.0]) is False


def test_detect_anomaly_false_on_short_series():
    assert detect_anomaly([90.0]) is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd api && pytest app/tests/services/test_anomaly_service.py -v`
Expected: FAIL — module not found.

- [ ] **Step 3: Implement the detector**

`api/app/services/anomaly_service.py`:
```python
from statistics import mean, pstdev

from app.config import get_intelligence_settings

_MIN_SAMPLES = 5


def zscore(samples: list[float], value: float) -> float:
    if len(samples) < 2:
        return 0.0
    sd = pstdev(samples)
    if sd == 0:
        return 0.0
    return (value - mean(samples)) / sd


def detect_anomaly(samples: list[float]) -> bool:
    if len(samples) < _MIN_SAMPLES:
        return False
    baseline, latest = samples[:-1], samples[-1]
    threshold = get_intelligence_settings().anomaly_z_threshold
    return zscore(baseline, latest) >= threshold
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd api && pytest app/tests/services/test_anomaly_service.py -v`
Expected: PASS (4 tests).

- [ ] **Step 5: Commit**

```bash
git add api/app/services/anomaly_service.py api/app/tests/services/test_anomaly_service.py
git commit -m "feat(intelligence): add EWMA/z-score anomaly detector"
```

---

## Task 5: Deterministic cause rules

**Files:**
- Create: `api/app/services/cause_rules.py`
- Test: `api/app/tests/services/test_cause_rules.py`

**Interfaces:**
- Consumes: `CauseCategory` (Task 2); a `CauseInput` dataclass defined here.
- Produces: `CauseInput` dataclass and `infer_cause(data: CauseInput) -> CauseCategory`. Rules applied in order: OOM→memory, exit≠0→crash, healthcheck fail→readiness, upstream-incident-first→cascade, sustained spike→resource, else undetermined.

- [ ] **Step 1: Write the failing test**

`api/app/tests/services/test_cause_rules.py`:
```python
from app.models import CauseCategory
from app.services.cause_rules import CauseInput, infer_cause


def _base(**kw) -> CauseInput:
    defaults = dict(
        oom_killed=False, exit_code=0, healthcheck_failed=False,
        upstream_incident_first=False, sustained_spike=False,
    )
    defaults.update(kw)
    return CauseInput(**defaults)


def test_oom_wins():
    assert infer_cause(_base(oom_killed=True, exit_code=137)) == CauseCategory.MEMORY


def test_nonzero_exit_is_crash():
    assert infer_cause(_base(exit_code=1)) == CauseCategory.CRASH


def test_healthcheck_is_readiness():
    assert infer_cause(_base(healthcheck_failed=True)) == CauseCategory.READINESS


def test_upstream_first_is_cascade():
    assert infer_cause(_base(upstream_incident_first=True)) == CauseCategory.CASCADE


def test_sustained_spike_is_resource():
    assert infer_cause(_base(sustained_spike=True)) == CauseCategory.RESOURCE


def test_no_rule_is_undetermined():
    assert infer_cause(_base()) == CauseCategory.UNDETERMINED
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd api && pytest app/tests/services/test_cause_rules.py -v`
Expected: FAIL — module not found.

- [ ] **Step 3: Implement the rules**

`api/app/services/cause_rules.py`:
```python
from dataclasses import dataclass

from app.models import CauseCategory


@dataclass(frozen=True)
class CauseInput:
    oom_killed: bool
    exit_code: int
    healthcheck_failed: bool
    upstream_incident_first: bool
    sustained_spike: bool


def infer_cause(data: CauseInput) -> CauseCategory:
    if data.oom_killed:
        return CauseCategory.MEMORY
    if data.exit_code != 0:
        return CauseCategory.CRASH
    if data.healthcheck_failed:
        return CauseCategory.READINESS
    if data.upstream_incident_first:
        return CauseCategory.CASCADE
    if data.sustained_spike:
        return CauseCategory.RESOURCE
    return CauseCategory.UNDETERMINED
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd api && pytest app/tests/services/test_cause_rules.py -v`
Expected: PASS (6 tests).

- [ ] **Step 5: Commit**

```bash
git add api/app/services/cause_rules.py api/app/tests/services/test_cause_rules.py
git commit -m "feat(intelligence): add ordered deterministic cause rules"
```

---

## Task 6: Narrative service (Ollama + template fallback)

**Files:**
- Create: `api/app/services/narrative_service.py`
- Test: `api/app/tests/services/test_narrative_service.py`

**Interfaces:**
- Consumes: `CauseCategory`, `NarrativeSource` (Task 2), `get_intelligence_settings()`.
- Produces: `async build_narrative(cause: CauseCategory, service: str, signals: list[str]) -> tuple[str, NarrativeSource]`. Returns a template string with `NarrativeSource.TEMPLATE` when Ollama disabled or on error; otherwise the Ollama text with `NarrativeSource.OLLAMA`.

- [ ] **Step 1: Write the failing test**

`api/app/tests/services/test_narrative_service.py`:
```python
import pytest

from app.models import CauseCategory, NarrativeSource
from app.services.narrative_service import build_narrative


@pytest.mark.asyncio
async def test_template_used_when_ollama_disabled(monkeypatch):
    from app.services import narrative_service as ns

    monkeypatch.setattr(
        ns, "_ollama_enabled", lambda: False
    )
    text, source = await build_narrative(
        CauseCategory.MEMORY, "db", ["mem 94%", "die OOMKilled"]
    )
    assert source is NarrativeSource.TEMPLATE
    assert "db" in text
    assert "memory" in text.lower()


@pytest.mark.asyncio
async def test_template_fallback_on_ollama_error(monkeypatch):
    from app.services import narrative_service as ns

    monkeypatch.setattr(ns, "_ollama_enabled", lambda: True)

    async def _boom(*a, **k):
        raise RuntimeError("connection refused")

    monkeypatch.setattr(ns, "_call_ollama", _boom)
    text, source = await build_narrative(CauseCategory.CRASH, "api", [])
    assert source is NarrativeSource.TEMPLATE
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd api && pytest app/tests/services/test_narrative_service.py -v`
Expected: FAIL — module not found.

- [ ] **Step 3: Implement the service**

`api/app/services/narrative_service.py`:
```python
import httpx

from app.config import get_intelligence_settings
from app.models import CauseCategory, NarrativeSource

_TEMPLATES = {
    CauseCategory.MEMORY: "Service {service} hit a memory limit ({signals}).",
    CauseCategory.CRASH: "Service {service} crashed with a non-zero exit ({signals}).",
    CauseCategory.READINESS: "Service {service} failed its healthcheck ({signals}).",
    CauseCategory.CASCADE: "Service {service} failed after an upstream dependency ({signals}).",
    CauseCategory.RESOURCE: "Service {service} saturated a resource ({signals}).",
    CauseCategory.UNDETERMINED: "Service {service} had an incident ({signals}).",
}


def _ollama_enabled() -> bool:
    return get_intelligence_settings().ollama_enabled


def _template(cause: CauseCategory, service: str, signals: list[str]) -> str:
    return _TEMPLATES[cause].format(
        service=service, signals=", ".join(signals) or "no signals"
    )


async def _call_ollama(prompt: str) -> str:
    s = get_intelligence_settings()
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.post(
            f"{s.ollama_url}/api/generate",
            json={"model": s.ollama_model, "prompt": prompt, "stream": False},
        )
        resp.raise_for_status()
        return resp.json()["response"].strip()


async def build_narrative(
    cause: CauseCategory, service: str, signals: list[str]
) -> tuple[str, NarrativeSource]:
    template = _template(cause, service, signals)
    if not _ollama_enabled():
        return template, NarrativeSource.TEMPLATE
    try:
        prompt = (
            "Summarize this Docker incident in one sentence. "
            f"Cause category: {cause}. Service: {service}. "
            f"Signals: {'; '.join(signals)}."
        )
        return await _call_ollama(prompt), NarrativeSource.OLLAMA
    except Exception:  # noqa: BLE001 — degrade to template on any Ollama failure
        return template, NarrativeSource.TEMPLATE
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd api && pytest app/tests/services/test_narrative_service.py -v`
Expected: PASS (2 tests).

- [ ] **Step 5: Commit**

```bash
git add api/app/services/narrative_service.py api/app/tests/services/test_narrative_service.py
git commit -m "feat(intelligence): add Ollama narrative with template fallback"
```

---

## Task 7: Incident correlation service

**Files:**
- Create: `api/app/services/incidents_service.py`
- Test: `api/app/tests/services/test_incidents_service.py`

**Interfaces:**
- Consumes: models (Task 2), `infer_cause`/`CauseInput` (Task 5), `build_narrative` (Task 6), `get_intelligence_settings()`, an `AsyncSession`.
- Produces:
  - `async correlate_trigger(session, trigger: Trigger) -> Incident` — creates or updates an incident, links signals, sets cause + narrative.
  - `async list_incidents(session, project: str | None, status: str | None, since: datetime | None) -> list[Incident]`.
  - `async get_incident(session, incident_id: int) -> Incident | None`.
  - `Trigger` dataclass: `container_id, service, project, ts, oom_killed, exit_code, healthcheck_failed, upstream_incident_first, sustained_spike, signal_summaries: list[str]`.

- [ ] **Step 1: Write the failing test**

`api/app/tests/services/test_incidents_service.py`:
```python
from datetime import UTC, datetime

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from testcontainers.postgres import PostgresContainer

from app.db.base import Base
from app.models import CauseCategory, IncidentStatus
from app.services.incidents_service import Trigger, correlate_trigger, list_incidents


@pytest.fixture
async def session():
    with PostgresContainer("timescale/timescaledb:latest-pg16") as pg:
        url = pg.get_connection_url().replace("psycopg2", "asyncpg")
        engine = create_async_engine(url)
        async with engine.begin() as conn:
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS timescaledb"))
            await conn.run_sync(Base.metadata.create_all)
        async with async_sessionmaker(engine)() as s:
            yield s
        await engine.dispose()


@pytest.mark.asyncio
async def test_oom_trigger_creates_memory_incident(session):
    trig = Trigger(
        container_id="abc", service="db", project="ai-aggregator",
        ts=datetime.now(UTC), oom_killed=True, exit_code=137,
        healthcheck_failed=False, upstream_incident_first=False,
        sustained_spike=False, signal_summaries=["mem 94%", "die OOMKilled"],
    )
    incident = await correlate_trigger(session, trig)
    assert incident.cause_category == CauseCategory.MEMORY
    assert incident.status == IncidentStatus.OPEN
    assert incident.narrative  # non-empty

    listed = await list_incidents(session, project="ai-aggregator", status=None, since=None)
    assert len(listed) == 1


@pytest.mark.asyncio
async def test_restart_loop_dedupes_into_one_incident(session):
    base = dict(
        container_id="abc", service="api", project="p", oom_killed=False,
        exit_code=1, healthcheck_failed=False, upstream_incident_first=False,
        sustained_spike=False, signal_summaries=["die exit 1"],
    )
    t1 = Trigger(ts=datetime.now(UTC), **base)
    await correlate_trigger(session, t1)
    t2 = Trigger(ts=datetime.now(UTC), **base)
    await correlate_trigger(session, t2)
    listed = await list_incidents(session, project=None, status=None, since=None)
    assert len(listed) == 1  # same open incident reused
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd api && pytest app/tests/services/test_incidents_service.py -v`
Expected: FAIL — module not found.

- [ ] **Step 3: Implement the service**

`api/app/services/incidents_service.py`:
```python
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    CauseCategory,
    Incident,
    IncidentSignal,
    IncidentStatus,
    SignalType,
)
from app.services.cause_rules import CauseInput, infer_cause
from app.services.narrative_service import build_narrative

_SEVERITY = {
    CauseCategory.MEMORY: "critical",
    CauseCategory.CRASH: "critical",
    CauseCategory.CASCADE: "critical",
    CauseCategory.READINESS: "warning",
    CauseCategory.RESOURCE: "warning",
    CauseCategory.UNDETERMINED: "info",
}


@dataclass(frozen=True)
class Trigger:
    container_id: str
    service: str
    project: str
    ts: datetime
    oom_killed: bool
    exit_code: int
    healthcheck_failed: bool
    upstream_incident_first: bool
    sustained_spike: bool
    signal_summaries: list[str]


async def _open_incident_for(session: AsyncSession, container_id: str) -> Incident | None:
    stmt = select(Incident).where(
        Incident.container_id == container_id,
        Incident.status == IncidentStatus.OPEN,
    )
    return (await session.execute(stmt)).scalars().first()


async def correlate_trigger(session: AsyncSession, trigger: Trigger) -> Incident:
    cause = infer_cause(
        CauseInput(
            oom_killed=trigger.oom_killed,
            exit_code=trigger.exit_code,
            healthcheck_failed=trigger.healthcheck_failed,
            upstream_incident_first=trigger.upstream_incident_first,
            sustained_spike=trigger.sustained_spike,
        )
    )
    incident = await _open_incident_for(session, trigger.container_id)
    if incident is None:
        narrative, source = await build_narrative(
            cause, trigger.service, trigger.signal_summaries
        )
        incident = Incident(
            opened_at=trigger.ts,
            closed_at=None,
            container_id=trigger.container_id,
            service=trigger.service,
            project=trigger.project,
            status=IncidentStatus.OPEN,
            severity=_SEVERITY[cause],
            cause_category=cause,
            narrative=narrative,
            narrative_source=source,
        )
        session.add(incident)
        await session.flush()
    for summary in trigger.signal_summaries:
        session.add(
            IncidentSignal(
                incident_id=incident.id,
                signal_type=SignalType.EVENT,
                ts=trigger.ts,
                summary=summary,
            )
        )
    await session.commit()
    await session.refresh(incident)
    return incident


async def list_incidents(
    session: AsyncSession,
    project: str | None,
    status: str | None,
    since: datetime | None,
) -> list[Incident]:
    stmt = select(Incident).order_by(Incident.opened_at.desc())
    if project:
        stmt = stmt.where(Incident.project == project)
    if status:
        stmt = stmt.where(Incident.status == status)
    if since:
        stmt = stmt.where(Incident.opened_at >= since)
    return list((await session.execute(stmt)).scalars().all())


async def get_incident(session: AsyncSession, incident_id: int) -> Incident | None:
    return await session.get(Incident, incident_id)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd api && pytest app/tests/services/test_incidents_service.py -v`
Expected: PASS (2 tests).

- [ ] **Step 5: Commit**

```bash
git add api/app/services/incidents_service.py api/app/tests/services/test_incidents_service.py
git commit -m "feat(intelligence): add incident correlation service with dedup"
```

---

## Task 8: Incident schemas + REST routes

**Files:**
- Create: `api/app/schemas/incident.py`, `api/app/routers/incidents.py`
- Modify: `api/app/main.py` (register router)
- Test: `api/app/tests/routers/test_incidents.py`

**Interfaces:**
- Consumes: `list_incidents`/`get_incident` (Task 7), `get_session` (Task 1), `get_current_user` (existing).
- Produces: `IncidentOut`, `IncidentDetailOut`, `SignalOut` Pydantic schemas; router at prefix `/api` with `GET /api/incidents` and `GET /api/incidents/{incident_id}`.

- [ ] **Step 1: Write the schemas**

`api/app/schemas/incident.py`:
```python
from datetime import datetime

from pydantic import BaseModel

from app.models import CauseCategory, IncidentStatus, NarrativeSource, SignalType


class SignalOut(BaseModel):
    signal_type: SignalType
    ts: datetime
    summary: str


class IncidentOut(BaseModel):
    id: int
    opened_at: datetime
    closed_at: datetime | None
    service: str
    project: str
    status: IncidentStatus
    severity: str
    cause_category: CauseCategory
    narrative: str
    narrative_source: NarrativeSource

    model_config = {"from_attributes": True}


class IncidentDetailOut(IncidentOut):
    signals: list[SignalOut]
```

- [ ] **Step 2: Write the failing test**

`api/app/tests/routers/test_incidents.py` (follow the existing router-test pattern in `api/app/tests/routers/`; override `get_session` and `get_current_user` dependencies with the testcontainer session + a fake user):
```python
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_list_incidents_empty(override_session, fake_user):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/incidents")
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_get_missing_incident_returns_404(override_session, fake_user):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/incidents/999")
    assert resp.status_code == 404
```
(Define `override_session` and `fake_user` fixtures in `api/app/tests/conftest.py`, reusing the Timescale container fixture from Task 7 and `app.dependency_overrides`.)

- [ ] **Step 3: Run test to verify it fails**

Run: `cd api && pytest app/tests/routers/test_incidents.py -v`
Expected: FAIL — route not registered (404 on list, or import error).

- [ ] **Step 4: Implement the router**

`api/app/routers/incidents.py`:
```python
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.incident import IncidentDetailOut, IncidentOut, SignalOut
from app.security import get_current_user
from app.services import incidents_service

router = APIRouter(prefix="/api", tags=["incidents"])


@router.get("/incidents", response_model=list[IncidentOut])
async def list_incidents(
    project: str | None = Query(default=None),
    status: str | None = Query(default=None),
    since: datetime | None = Query(default=None),
    session: AsyncSession = Depends(get_session),
    _user: object = Depends(get_current_user),
) -> list[IncidentOut]:
    rows = await incidents_service.list_incidents(session, project, status, since)
    return [IncidentOut.model_validate(r) for r in rows]


@router.get("/incidents/{incident_id}", response_model=IncidentDetailOut)
async def get_incident(
    incident_id: int,
    session: AsyncSession = Depends(get_session),
    _user: object = Depends(get_current_user),
) -> IncidentDetailOut:
    incident = await incidents_service.get_incident(session, incident_id)
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    signals = [SignalOut.model_validate(s, from_attributes=True) for s in incident.signals]
    detail = IncidentDetailOut.model_validate(incident)
    detail.signals = signals
    return detail
```
Add relationship on `Incident` (Task 2 model) if needed for `.signals`:
```python
from sqlalchemy.orm import relationship
signals: Mapped[list["IncidentSignal"]] = relationship(lazy="selectin")
```
Register in `api/app/main.py`: `from app.routers import incidents` then `app.include_router(incidents.router)`.

- [ ] **Step 5: Run test to verify it passes**

Run: `cd api && pytest app/tests/routers/test_incidents.py -v`
Expected: PASS (2 tests).

- [ ] **Step 6: Commit**

```bash
git add api/app/schemas/incident.py api/app/routers/incidents.py api/app/main.py api/app/models/incident.py api/app/tests/routers/test_incidents.py api/app/tests/conftest.py
git commit -m "feat(api): add incident list + detail REST endpoints"
```

---

## Task 9: Collector — event consumer + stats poller + supervisor

**Files:**
- Create: `api/app/collector/__init__.py`, `event_consumer.py`, `stats_poller.py`, `log_tailer.py`, `supervisor.py`
- Modify: `api/app/main.py` (start/stop tasks in lifespan)
- Test: `api/app/tests/collector/test_event_consumer.py`, `test_stats_poller.py`, `test_supervisor.py`

**Interfaces:**
- Consumes: `docker_client` (existing `services/docker_client.py`), models (Task 2), `correlate_trigger` (Task 7), `detect_anomaly` (Task 4), `AsyncSessionLocal` (Task 1), `get_intelligence_settings()`.
- Produces:
  - `normalize_event(raw: dict) -> DockerEvent | None` (returns None for irrelevant types).
  - `async run_event_consumer(stop: asyncio.Event) -> None`.
  - `async poll_once(session) -> list[MetricSample]`.
  - `async run_stats_poller(stop: asyncio.Event) -> None`.
  - `class CollectorSupervisor` with `async start()` / `async stop()`.

- [ ] **Step 1: Write the failing test for the normalizer**

`api/app/tests/collector/test_event_consumer.py`:
```python
from app.collector.event_consumer import normalize_event
from app.models import DockerEventType


def test_normalize_die_event():
    raw = {
        "Type": "container", "Action": "die", "time": 1_700_000_000,
        "Actor": {"ID": "abc", "Attributes": {
            "exitCode": "137",
            "com.docker.compose.project": "p",
            "com.docker.compose.service": "db",
        }},
    }
    event = normalize_event(raw)
    assert event is not None
    assert event.type == DockerEventType.DIE
    assert event.exit_code == 137
    assert event.project == "p"


def test_normalize_ignores_irrelevant_action():
    assert normalize_event({"Type": "container", "Action": "exec_start"}) is None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd api && pytest app/tests/collector/test_event_consumer.py -v`
Expected: FAIL — module not found.

- [ ] **Step 3: Implement the normalizer + consumer**

`api/app/collector/event_consumer.py`:
```python
import asyncio
from datetime import UTC, datetime

from app.models import DockerEvent, DockerEventType
from app.services.docker_client import get_docker_client

_RELEVANT = {t.value for t in DockerEventType}


def normalize_event(raw: dict) -> DockerEvent | None:
    action = raw.get("Action", "")
    if action not in _RELEVANT:
        return None
    actor = raw.get("Actor", {})
    attrs = actor.get("Attributes", {})
    exit_code = attrs.get("exitCode")
    ts = datetime.fromtimestamp(raw.get("time", 0), tz=UTC)
    return DockerEvent(
        ts=ts,
        container_id=actor.get("ID", ""),
        service=attrs.get("com.docker.compose.service", ""),
        project=attrs.get("com.docker.compose.project", ""),
        type=DockerEventType(action),
        exit_code=int(exit_code) if exit_code is not None else None,
        health=attrs.get("health_status"),
    )


async def run_event_consumer(stop: asyncio.Event) -> None:
    client = get_docker_client()
    while not stop.is_set():
        try:
            for raw in client.events(decode=True):
                if stop.is_set():
                    break
                event = normalize_event(raw)
                if event is not None:
                    await _persist_and_correlate(event)
        except Exception:  # noqa: BLE001 — reconnect on stream loss
            await asyncio.sleep(2)
```
Implement `_persist_and_correlate(event)` to open an `AsyncSessionLocal`, persist the event, build a `Trigger` (oom detected via `type == OOM` or exit 137, exit_code, healthcheck), and call `correlate_trigger`. (Show full code when implementing; keep the function ≤ 50 lines by delegating trigger-building to a helper.)

- [ ] **Step 4: Write the stats-poller test**

`api/app/tests/collector/test_stats_poller.py`:
```python
import pytest

from app.collector.stats_poller import compute_sample


def test_compute_sample_from_stats():
    stats = {
        "cpu_stats": {"cpu_usage": {"total_usage": 200}, "system_cpu_usage": 1000, "online_cpus": 2},
        "precpu_stats": {"cpu_usage": {"total_usage": 100}, "system_cpu_usage": 800},
        "memory_stats": {"usage": 500, "limit": 1000},
        "networks": {"eth0": {"rx_bytes": 10, "tx_bytes": 20}},
        "blkio_stats": {"io_service_bytes_recursive": [
            {"op": "read", "value": 5}, {"op": "write", "value": 7}]},
    }
    sample = compute_sample("abc", stats)
    assert sample.container_id == "abc"
    assert sample.mem_pct == pytest.approx(50.0)
    assert sample.cpu_pct > 0
```

- [ ] **Step 5: Run stats test to verify it fails, then implement**

Run: `cd api && pytest app/tests/collector/test_stats_poller.py -v` → FAIL.
Implement `api/app/collector/stats_poller.py` with `compute_sample(container_id, stats) -> MetricSample` (reuse the CPU delta math already in `routers/metrics.py`), `poll_once(session)` iterating running containers with bounded concurrency (`asyncio.Semaphore`), and `run_stats_poller(stop)` looping every `collector_stats_interval_s`. Re-run → PASS.

- [ ] **Step 6: Write the supervisor test**

`api/app/tests/collector/test_supervisor.py`:
```python
import asyncio

import pytest

from app.collector.supervisor import CollectorSupervisor


@pytest.mark.asyncio
async def test_supervisor_restarts_crashed_task():
    calls = {"n": 0}

    async def flaky(stop: asyncio.Event) -> None:
        calls["n"] += 1
        if calls["n"] == 1:
            raise RuntimeError("boom")
        await stop.wait()

    sup = CollectorSupervisor(tasks=[flaky], restart_delay_s=0)
    await sup.start()
    await asyncio.sleep(0.05)
    await sup.stop()
    assert calls["n"] >= 2  # restarted after the crash
```

- [ ] **Step 7: Run supervisor test to verify it fails, then implement**

Run: `cd api && pytest app/tests/collector/test_supervisor.py -v` → FAIL.
Implement `api/app/collector/supervisor.py`: `CollectorSupervisor(tasks, restart_delay_s)` wraps each coroutine factory in a loop that restarts it on exception until `stop` is set; `start()` schedules them, `stop()` sets the event and awaits. Re-run → PASS.

- [ ] **Step 8: Wire into lifespan**

In `api/app/main.py`, add a lifespan handler that instantiates `CollectorSupervisor(tasks=[run_event_consumer, run_stats_poller])`, calls `await sup.start()` on startup and `await sup.stop()` on shutdown. Guard with a setting so tests can disable it.

- [ ] **Step 9: Run the full collector suite**

Run: `cd api && pytest app/tests/collector -v`
Expected: PASS (all collector tests).

- [ ] **Step 10: Commit**

```bash
git add api/app/collector api/app/main.py api/app/tests/collector
git commit -m "feat(collector): add event consumer, stats poller, and supervised lifespan tasks"
```

---

## Task 10: WebSocket live incident stream

**Files:**
- Modify: `api/app/routers/incidents.py` (add WS route), `api/app/services/incidents_service.py` (add an in-process publisher)
- Test: `api/app/tests/routers/test_incidents_ws.py`

**Interfaces:**
- Consumes: `verify_token` (existing, used by `routers/logs.py`).
- Produces: `WS /api/incidents/stream`; `incident_publisher` (an `asyncio`-based fan-out) with `subscribe()` / `publish(incident_id: int)`.

- [ ] **Step 1: Write the failing test**

`api/app/tests/routers/test_incidents_ws.py`:
```python
import pytest
from starlette.testclient import TestClient

from app.main import app


def test_ws_rejects_missing_token():
    client = TestClient(app)
    with pytest.raises(Exception):
        with client.websocket_connect("/api/incidents/stream"):
            pass


def test_ws_pushes_published_incident(valid_token, monkeypatch):
    client = TestClient(app)
    with client.websocket_connect(f"/api/incidents/stream?token={valid_token}") as ws:
        from app.services.incidents_service import incident_publisher

        incident_publisher.publish(42)
        msg = ws.receive_json()
        assert msg["incident_id"] == 42
```
(`valid_token` fixture mints a token via the existing `create_access_token`.)

- [ ] **Step 2: Run test to verify it fails**

Run: `cd api && pytest app/tests/routers/test_incidents_ws.py -v`
Expected: FAIL — route/publisher missing.

- [ ] **Step 3: Implement publisher + WS route**

In `incidents_service.py` add a module-level `incident_publisher` with an `asyncio.Queue` per subscriber (`subscribe()` returns a queue, `publish(id)` puts on all queues). Call `incident_publisher.publish(incident.id)` at the end of `correlate_trigger`.
In `routers/incidents.py` add:
```python
@router.websocket("/incidents/stream")
async def incidents_stream(websocket: WebSocket, token: str = Query(...)) -> None:
    if not verify_token(token):
        await websocket.close(code=4001)
        return
    await websocket.accept()
    queue = incident_publisher.subscribe()
    try:
        while True:
            incident_id = await queue.get()
            await websocket.send_json({"incident_id": incident_id})
    except WebSocketDisconnect:
        incident_publisher.unsubscribe(queue)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd api && pytest app/tests/routers/test_incidents_ws.py -v`
Expected: PASS (2 tests).

- [ ] **Step 5: Commit**

```bash
git add api/app/routers/incidents.py api/app/services/incidents_service.py api/app/tests/routers/test_incidents_ws.py
git commit -m "feat(api): add live incident WebSocket stream"
```

---

## Task 11: Frontend — incidents domain (types + queries)

**Files:**
- Create: `code/src/domain/incidents/types.ts`, `code/src/domain/incidents/queries.ts`
- Test: `code/src/domain/incidents/queries.test.ts`

**Interfaces:**
- Consumes: the Axios client `api/http/client.ts` (existing).
- Produces: `Incident`, `IncidentDetail`, `Signal` types; `useIncidents(filters)`, `useIncident(id)` TanStack hooks; `incidentsKeys` query-key factory.

- [ ] **Step 1: Write the types**

`code/src/domain/incidents/types.ts`:
```typescript
export type CauseCategory =
  | "memory" | "crash" | "readiness" | "cascade" | "resource" | "undetermined";
export type IncidentStatus = "open" | "resolved";
export type SignalType = "event" | "metric" | "log";

export interface Signal {
  signal_type: SignalType;
  ts: string;
  summary: string;
}

export interface Incident {
  id: number;
  opened_at: string;
  closed_at: string | null;
  service: string;
  project: string;
  status: IncidentStatus;
  severity: "critical" | "warning" | "info";
  cause_category: CauseCategory;
  narrative: string;
  narrative_source: "ollama" | "template";
}

export interface IncidentDetail extends Incident {
  signals: Signal[];
}

export interface IncidentFilters {
  project?: string;
  status?: IncidentStatus;
}
```

- [ ] **Step 2: Write the failing test**

`code/src/domain/incidents/queries.test.ts`:
```typescript
import { describe, expect, it } from "vitest";
import { incidentsKeys } from "./queries";

describe("incidentsKeys", () => {
  it("builds a list key including filters", () => {
    expect(incidentsKeys.list({ project: "p" })).toEqual([
      "incidents", "list", { project: "p" },
    ]);
  });
  it("builds a detail key", () => {
    expect(incidentsKeys.detail(7)).toEqual(["incidents", "detail", 7]);
  });
});
```

- [ ] **Step 3: Run test to verify it fails**

Run: `cd code && npx vitest run src/domain/incidents/queries.test.ts`
Expected: FAIL — module not found.

- [ ] **Step 4: Implement queries**

`code/src/domain/incidents/queries.ts`:
```typescript
import { useQuery } from "@tanstack/react-query";
import { httpClient } from "../../api/http/client";
import type { Incident, IncidentDetail, IncidentFilters } from "./types";

export const incidentsKeys = {
  all: ["incidents"] as const,
  list: (filters: IncidentFilters) => ["incidents", "list", filters] as const,
  detail: (id: number) => ["incidents", "detail", id] as const,
};

export function useIncidents(filters: IncidentFilters) {
  return useQuery({
    queryKey: incidentsKeys.list(filters),
    queryFn: async () => {
      const { data } = await httpClient.get<Incident[]>("/api/incidents", {
        params: filters,
      });
      return data;
    },
    refetchInterval: 5_000,
  });
}

export function useIncident(id: number) {
  return useQuery({
    queryKey: incidentsKeys.detail(id),
    queryFn: async () => {
      const { data } = await httpClient.get<IncidentDetail>(`/api/incidents/${id}`);
      return data;
    },
  });
}
```

- [ ] **Step 5: Run test to verify it passes**

Run: `cd code && npx vitest run src/domain/incidents/queries.test.ts`
Expected: PASS (2 tests).

- [ ] **Step 6: Commit**

```bash
git add code/src/domain/incidents
git commit -m "feat(web): add incidents domain types and TanStack query hooks"
```

---

## Task 12: Frontend — feed, detail, timeline, cause banner + route

**Files:**
- Create: `code/src/features/incidents/IncidentsFeed.tsx`, `IncidentDetail.tsx`, `IncidentTimeline.tsx`, `CauseBanner.tsx` (+ SCSS modules)
- Create: `code/src/pages/Incidents.tsx`
- Modify: `code/src/App.tsx` (lazy route `/incidents`), navigation component
- Test: `code/src/features/incidents/IncidentTimeline.test.tsx`, `CauseBanner.test.tsx`

**Interfaces:**
- Consumes: `useIncidents`, `useIncident` (Task 11), types (Task 11), existing topology components for the involved-services mini-graph, Recharts for mini-charts.
- Produces: route-level `<Incidents />`; presentational `<IncidentTimeline signals={...} />` and `<CauseBanner incident={...} />`.

- [ ] **Step 1: Write the CauseBanner test**

`code/src/features/incidents/CauseBanner.test.tsx`:
```typescript
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CauseBanner } from "./CauseBanner";
import type { Incident } from "../../domain/incidents/types";

const incident: Incident = {
  id: 1, opened_at: "2026-07-19T14:32:07Z", closed_at: null,
  service: "db", project: "ai-aggregator", status: "open",
  severity: "critical", cause_category: "memory",
  narrative: "Service db hit a memory limit.", narrative_source: "template",
};

describe("CauseBanner", () => {
  it("renders the cause category and narrative", () => {
    render(<CauseBanner incident={incident} />);
    expect(screen.getByText(/memory/i)).toBeInTheDocument();
    expect(screen.getByText(/hit a memory limit/i)).toBeInTheDocument();
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd code && npx vitest run src/features/incidents/CauseBanner.test.tsx`
Expected: FAIL — component not found.

- [ ] **Step 3: Implement CauseBanner + IncidentTimeline**

`CauseBanner.tsx` renders a severity chip + `cause_category` label + `narrative` (semantic `<section>`, `aria-label="Probable cause"`).
`IncidentTimeline.tsx` maps `signals` to a `<ol>` of rows: time, a color dot keyed by `signal_type` (event=critical, metric=warning, log=info), and the summary. Colors from SCSS variables; ensure WCAG AA contrast; dark-mode aware.

- [ ] **Step 4: Write the IncidentTimeline test**

`code/src/features/incidents/IncidentTimeline.test.tsx`:
```typescript
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { IncidentTimeline } from "./IncidentTimeline";

describe("IncidentTimeline", () => {
  it("renders one row per signal in order", () => {
    render(
      <IncidentTimeline
        signals={[
          { signal_type: "metric", ts: "2026-07-19T14:31:58Z", summary: "mem 94%" },
          { signal_type: "event", ts: "2026-07-19T14:32:07Z", summary: "die OOMKilled" },
        ]}
      />,
    );
    const items = screen.getAllByRole("listitem");
    expect(items).toHaveLength(2);
    expect(items[0]).toHaveTextContent("mem 94%");
  });
});
```

- [ ] **Step 5: Run test to verify it passes**

Run: `cd code && npx vitest run src/features/incidents`
Expected: PASS.

- [ ] **Step 6: Implement feed, detail page, and route**

`IncidentsFeed.tsx` uses `useIncidents(filters)` with a project `<select>` filter; each row links to detail. `IncidentDetail.tsx` uses `useIncident(id)`, renders `<CauseBanner>` + `<IncidentTimeline>` + involved-services mini-graph + Recharts mini-charts. `pages/Incidents.tsx` composes feed/detail via nested routes. Add lazy route in `App.tsx`: `/incidents` and `/incidents/:incidentId`; add a nav link.

- [ ] **Step 7: Run frontend build + lint**

Run: `cd code && npm run build && npm run lint`
Expected: build succeeds, 0 lint errors.

- [ ] **Step 8: Commit**

```bash
git add code/src/features/incidents code/src/pages/Incidents.tsx code/src/App.tsx
git commit -m "feat(web): add incidents feed, detail, timeline, and route"
```

---

## Task 13: E2E, docker-compose Timescale service, coverage gate

**Files:**
- Create: `code/e2e/tests/incidents.spec.ts`
- Modify: `docker-compose.yml` (add `db` timescale service + `DATABASE_URL`), `api/pyproject.toml` (`fail_under = 85`), `README.md`, `CLAUDE.md` (correct stale notes)
- Test: the e2e spec itself

**Interfaces:**
- Consumes: the full stack.

- [ ] **Step 1: Add the Timescale service to compose**

In `docker-compose.yml` add:
```yaml
  db:
    image: timescale/timescaledb:latest-pg16
    environment:
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: overview
    volumes:
      - overview_db:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
```
Add `overview_db:` under `volumes:`, set `DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/overview` on the `api` service, and `depends_on: [db]`.

- [ ] **Step 2: Write the E2E spec**

`code/e2e/tests/incidents.spec.ts`:
```typescript
import { expect, test } from "@playwright/test";
import { login } from "./helpers/auth";

test("incidents page renders a seeded incident with cause and timeline", async ({ page }) => {
  await login(page);
  await page.goto("/incidents");
  await expect(page.getByRole("heading", { name: /incidents/i })).toBeVisible();
  await page.getByRole("link", { name: /db/i }).first().click();
  await expect(page.getByLabel(/probable cause/i)).toBeVisible();
  await expect(page.getByRole("listitem")).not.toHaveCount(0);
});
```
(Seed one incident via an API call in a Playwright `beforeEach`, or a small seed script mirroring `app/demo.py`.)

- [ ] **Step 3: Run E2E**

Run: `make dev-up && cd code && npx playwright test e2e/tests/incidents.spec.ts`
Expected: PASS.

- [ ] **Step 4: Raise the coverage gate + fix stale docs**

Set `fail_under = 85` in `api/pyproject.toml`. Update `CLAUDE.md`: remove the "python-jose CVE" known-issue (already PyJWT), correct FastAPI/version notes, add the DB stack + incident feature. Add an `/incidents` section to `README.md`.

- [ ] **Step 5: Run the full gate**

Run: `cd api && make ci` and `cd code && npm run build && npm run lint`
Expected: coverage ≥ 85%, lint 0, build OK.

- [ ] **Step 6: Commit**

```bash
git add docker-compose.yml api/pyproject.toml README.md CLAUDE.md code/e2e/tests/incidents.spec.ts
git commit -m "feat(intelligence): wire Timescale service, e2e, and raise coverage gate to 85"
```

---

## Self-Review

**Spec coverage:**
- §5.1 collector → Task 9 · correlation service → Task 7 · narrative → Task 6 · cause rules → Task 5 · anomaly → Task 4 ✓
- §5.1 API REST → Task 8 · WS → Task 10 ✓
- §5.1 frontend feed/detail/timeline/route → Tasks 11–12 ✓
- §6 data model + hypertable → Task 2 · external config → Task 3 ✓
- §6.1 cause rules ordered → Task 5 (6 tests, one per rule) ✓
- §7 error handling: docker.sock retry → Task 9 consumer loop · Ollama fallback → Task 6 · collector crash restart → Task 9 supervisor · Timescale fail-fast → Task 2 migration guard ✓
- §8 testing: unit (4,5,6), integration (2,7,9), frontend (11,12), e2e (13) ✓
- §9 config keys → Task 3 YAML + Global Constraints ✓
- Separate track (rename/Notion) correctly excluded ✓

**Placeholder scan:** Steps that delegate full code (Task 9 `_persist_and_correlate`, stats poller body, supervisor body; Task 12 feed/detail bodies) name exact functions, signatures, files, and the reuse source — acceptable decomposition, not blank placeholders. No "TBD"/"add error handling"/"write tests for the above" left.

**Type consistency:** `Trigger`, `CauseInput`, `CauseCategory`, `NarrativeSource`, `IncidentStatus`, `SignalType`, `IncidentOut`/`IncidentDetailOut`, `incidentsKeys`, `useIncidents`/`useIncident` used consistently across tasks. `correlate_trigger`/`list_incidents`/`get_incident` signatures match between Tasks 7, 8, 10.
