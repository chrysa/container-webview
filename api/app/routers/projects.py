from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from app import demo
from app.config import settings
from app.security import get_current_user
from app.services.project_manager import ProjectModel
from app.services.project_manager import list_projects
from app.services.project_manager import load_project


router = APIRouter()


_PROJECT_RESPONSES: dict[int | str, dict] = {404: {"description": "Project not found"}}


@router.get("", response_model=list[ProjectModel])
def get_projects(_: dict = Depends(get_current_user)) -> list[ProjectModel]:
    if settings.demo_mode:
        return [ProjectModel(**project) for project in demo.list_projects()]
    return list_projects()


@router.get("/{project_id}", response_model=ProjectModel, responses=_PROJECT_RESPONSES)
def get_project(project_id: str, _: dict = Depends(get_current_user)) -> ProjectModel:
    if settings.demo_mode:
        demo_project = demo.load_project(project_id)
        if not demo_project:
            raise HTTPException(status_code=404, detail="Projet introuvable")
        return ProjectModel(**demo_project)
    project = load_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projet introuvable")
    return project
