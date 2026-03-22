from typing import Annotated

from fastapi import APIRouter, Depends

from app.security import security
from app.services.alerts_service import Alert, alerts_service

router = APIRouter()


@router.get("")
def get_alerts(
    _: Annotated[dict, Depends(security.get_current_user)]
) -> list[Alert]:
    """Return all operational alerts across every running container."""
    return alerts_service.get_all()


@router.get("/project/{project_id}")
def get_project_alerts(
    project_id: str,
    _: Annotated[dict, Depends(security.get_current_user)],
) -> list[Alert]:
    """Return alerts filtered to a specific Compose project."""
    return alerts_service.get_for_project(project_id)
