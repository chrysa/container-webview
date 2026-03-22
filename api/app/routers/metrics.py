from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from app.constants import ERR_PROJECT_NOT_FOUND
from app.security import security
from app.services.metrics_service import ServiceMetrics
from app.services.metrics_service import metrics_service
from app.services.project_manager import project_manager

router = APIRouter()

_NOT_FOUND = {404: {"description": ERR_PROJECT_NOT_FOUND}}


@router.get("/{project_id}/metrics", responses=_NOT_FOUND)
def get_metrics(
    project_id: str,
    _: Annotated[dict, Depends(security.get_current_user)],
) -> list[ServiceMetrics]:
    """Return real-time resource metrics for all containers in a project."""
    if not project_manager.load(project_id):
        raise HTTPException(status_code=404, detail=ERR_PROJECT_NOT_FOUND)
    return metrics_service.get_project_metrics(project_id)
