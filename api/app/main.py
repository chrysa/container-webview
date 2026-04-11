from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import alerts
from app.routers import auth
from app.routers import lifecycle
from app.routers import logs
from app.routers import metrics
from app.routers import projects
from app.routers import topology


app = FastAPI(title="Docker Overview API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router,      prefix="/api/auth",     tags=["auth"])
app.include_router(projects.router,  prefix="/api/projects", tags=["projects"])
app.include_router(topology.router,  prefix="/api/projects", tags=["topology"])
app.include_router(lifecycle.router, prefix="/api/projects", tags=["lifecycle"])
app.include_router(logs.router,      prefix="/api/projects", tags=["logs"])
app.include_router(metrics.router,   prefix="/api/projects", tags=["metrics"])
app.include_router(alerts.router,    prefix="/api/alerts",   tags=["alerts"])


@app.get("/api")
def ping():
    return {"status": "ok"}
