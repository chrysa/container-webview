from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from app.security import get_current_user
from app.services.project_manager import ProjectModel
from app.services.project_manager import list_projects
from app.services.project_manager import load_project


router = APIRouter()


@router.get("", response_model=list[ProjectModel])
def get_projects(_: dict = Depends(get_current_user)) -> list[ProjectModel]:
    return list_projects()


@router.get("/{project_id}", response_model=ProjectModel)
def get_project(project_id: str, _: dict = Depends(get_current_user)) -> ProjectModel:
    project = load_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projet introuvable")
    return project
