from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.constants import ERR_PROJECT_NOT_FOUND
from app.security import security
from app.services.project_manager import ProjectModel, project_manager

router = APIRouter()

_CurrentUser = Annotated[dict, Depends(security.get_current_user)]
_NOT_FOUND = {404: {"description": ERR_PROJECT_NOT_FOUND}}


@router.get("", responses=_NOT_FOUND)
def get_projects(_: _CurrentUser) -> list[ProjectModel]:
    """List all discovered Compose projects."""
    return project_manager.list_all()


@router.get("/{project_id}", responses=_NOT_FOUND)
def get_project(project_id: str, _: _CurrentUser) -> ProjectModel:
    """Return a single Compose project by ID."""
    project = project_manager.load(project_id)
    if not project:
        raise HTTPException(status_code=404, detail=ERR_PROJECT_NOT_FOUND)
    return project
