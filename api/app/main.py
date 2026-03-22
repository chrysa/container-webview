from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import alerts, auth, lifecycle, logs, metrics, projects, topology

_API_PROJECTS = "/api/projects"

app = FastAPI(title="Docker Overview API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router,      prefix="/api/auth",        tags=["auth"])
app.include_router(projects.router,  prefix=_API_PROJECTS,      tags=["projects"])
app.include_router(topology.router,  prefix=_API_PROJECTS,      tags=["topology"])
app.include_router(lifecycle.router, prefix=_API_PROJECTS,      tags=["lifecycle"])
app.include_router(logs.router,      prefix=_API_PROJECTS,      tags=["logs"])
app.include_router(metrics.router,   prefix=_API_PROJECTS,      tags=["metrics"])
app.include_router(alerts.router,    prefix="/api/alerts",      tags=["alerts"])


@app.get("/api")
def ping() -> dict:
    return {"status": "ok"}
