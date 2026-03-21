from fastapi import APIRouter, HTTPException, Depends
from typing import List

from app.security import get_current_user
from app.services.project_manager import list_projects, load_project, ProjectModel

router = APIRouter()


@router.get("", response_model=List[ProjectModel])
def get_projects(_: dict = Depends(get_current_user)):
    return list_projects()


@router.get("/{project_id}", response_model=ProjectModel)
def get_project(project_id: str, _: dict = Depends(get_current_user)):
    project = load_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projet introuvable")
    return project
