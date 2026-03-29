from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_redoc_html
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse

from app.config import get_settings
from app.constants import API_V1_PREFIX
from app.constants import OAUTH2_TOKEN_URL
from app.routers import alerts
from app.routers import auth
from app.routers import lifecycle
from app.routers import logs
from app.routers import metrics
from app.routers import projects
from app.routers import topology

_V1_PROJECTS = f"{API_V1_PREFIX}/projects"

# ── Metadata OpenAPI ────────────────────────────────────────────────────────

_DESCRIPTION = """\
REST API for the **Docker Overview WebUI** — manage and monitor Docker Compose projects.

## Authentication

All `/api/v1/` endpoints require a **JWT Bearer token**.  
Obtain one via `POST /api/v1/auth/login` (OAuth2 password flow).

## HATEOAS

Every response embeds a `_links` object so clients can navigate related resources \
without constructing URLs by hand.

## Versioning

Current version: **v1** — prefix `/api/v1/`.
"""

_OPENAPI_TAGS: list[dict] = [
    {
        "name": "health",
        "description": "Liveness / readiness — no authentication required.",
    },
    {
        "name": "auth",
        "description": "JWT authentication (OAuth2 password flow).",
    },
    {
        "name": "projects",
        "description": "Discover and inspect Docker Compose projects.",
    },
    {
        "name": "metrics",
        "description": "Real-time container resource metrics (CPU, RAM, network, I/O).",
    },
    {
        "name": "alerts",
        "description": "Operational alerts derived from container states.",
    },
    {
        "name": "topology",
        "description": "Service dependency graph for a Compose project.",
    },
    {
        "name": "lifecycle",
        "description": "Container lifecycle actions: start, stop, restart, pause, unpause.",
    },
    {
        "name": "logs",
        "description": "Live container log streaming over WebSocket.",
    },
]

# ── Application ─────────────────────────────────────────────────────────────

app = FastAPI(
    title="Docker Overview API",
    version="1.0.0",
    description=_DESCRIPTION,
    docs_url=None,
    redoc_url=None,
    openapi_url="/api/openapi.json",
    contact={
        "name": "Docker Overview WebUI",
        "url": "https://github.com/chrysa/container-webview",
    },
    license_info={"name": "MIT"},
    openapi_tags=_OPENAPI_TAGS,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router,      prefix=f"{API_V1_PREFIX}/auth",     tags=["auth"])
app.include_router(projects.router,  prefix=_V1_PROJECTS,                tags=["projects"])
app.include_router(topology.router,  prefix=_V1_PROJECTS,                tags=["topology"])
app.include_router(lifecycle.router, prefix=_V1_PROJECTS,                tags=["lifecycle"])
app.include_router(logs.router,      prefix=_V1_PROJECTS,                tags=["logs"])
app.include_router(metrics.router,   prefix=_V1_PROJECTS,                tags=["metrics"])
app.include_router(alerts.router,    prefix=f"{API_V1_PREFIX}/alerts",   tags=["alerts"])

# ── Public endpoints ─────────────────────────────────────────────────────────


@app.get("/health", tags=["health"], include_in_schema=True)
def health() -> dict:
    """Liveness probe — no authentication required."""
    return {
        "status": "ok",
        "version": "1.0.0",
        "_links": {
            "docs":     {"href": "/api/docs"},
            "redoc":    {"href": "/api/redoc"},
            "openapi":  {"href": "/api/openapi.json"},
            "projects": {"href": f"{API_V1_PREFIX}/projects"},
            "alerts":   {"href": f"{API_V1_PREFIX}/alerts"},
            "login":    {"href": OAUTH2_TOKEN_URL},
        },
    }


@app.get("/api/docs", include_in_schema=False)
def swagger_ui() -> HTMLResponse:
    """Swagger UI with version selector."""
    return get_swagger_ui_html(
        openapi_url="/api/openapi.json",
        title="Docker Overview API",
        swagger_ui_parameters={
            "urls": [
                {"url": "/api/openapi.json", "name": "v1 (actuel)"},
            ],
            "urls.primaryName": "v1 (actuel)",
            "persistAuthorization": True,
            "displayRequestDuration": True,
            "docExpansion": "list",
            "filter": True,
        },
    )


@app.get("/api/redoc", include_in_schema=False)
def redoc_html() -> HTMLResponse:
    """ReDoc documentation."""
    return get_redoc_html(
        openapi_url="/api/openapi.json",
        title="Docker Overview API",
        with_google_fonts=False,
    )
