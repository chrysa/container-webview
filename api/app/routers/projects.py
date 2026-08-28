from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from app.constants import API_V1_PREFIX
from app.constants import ERR_PROJECT_NOT_FOUND
from app.constants import RESPONSES_NOT_FOUND
from app.models.hateoas import HateoasLink
from app.models.hateoas import ProjectLinks
from app.security import security
from app.services.project_manager import ProjectModel
from app.services.project_manager import project_manager


router = APIRouter()

_CurrentUser = Annotated[dict, Depends(security.get_current_user)]


def _add_project_links(project: ProjectModel) -> ProjectModel:
    """Attach HATEOAS navigation links to a ProjectModel instance."""
    pid = project.id
    project.links = ProjectLinks(
        self=HateoasLink(href=f"{API_V1_PREFIX}/projects/{pid}"),
        topology=HateoasLink(href=f"{API_V1_PREFIX}/projects/{pid}/topology"),
        metrics=HateoasLink(href=f"{API_V1_PREFIX}/projects/{pid}/metrics"),
        alerts=HateoasLink(href=f"{API_V1_PREFIX}/alerts/project/{pid}"),
    )
    return project


@router.get("", response_model=list[ProjectModel], responses=RESPONSES_NOT_FOUND)
def get_projects(_: _CurrentUser) -> list[ProjectModel]:
    """List all discovered Compose projects."""
    return [_add_project_links(p) for p in project_manager.list_all()]


@router.get("/{project_id}", response_model=ProjectModel, responses=RESPONSES_NOT_FOUND)
def get_project(project_id: str, _: _CurrentUser) -> ProjectModel:
    """Return a single Compose project by ID."""
    project = project_manager.load(project_id)
    if not project:
        raise HTTPException(status_code=404, detail=ERR_PROJECT_NOT_FOUND)
    return _add_project_links(project)
