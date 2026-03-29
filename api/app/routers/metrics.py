from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from app.constants import API_V1_PREFIX
from app.constants import ERR_PROJECT_NOT_FOUND
from app.models.hateoas import HateoasLink
from app.models.hateoas import MetricsLinks
from app.security import security
from app.services.metrics_service import ServiceMetrics
from app.services.metrics_service import metrics_service
from app.services.project_manager import project_manager

router = APIRouter()

_NOT_FOUND = {404: {"description": ERR_PROJECT_NOT_FOUND}}


def _add_metrics_links(metrics: ServiceMetrics, project_id: str) -> ServiceMetrics:
    """Attach HATEOAS navigation links to a ServiceMetrics instance."""
    metrics.links = MetricsLinks(
        self=HateoasLink(href=f"{API_V1_PREFIX}/projects/{project_id}/metrics"),
        project=HateoasLink(href=f"{API_V1_PREFIX}/projects/{project_id}"),
    )
    return metrics


@router.get("/{project_id}/metrics", responses=_NOT_FOUND)
def get_metrics(
    project_id: str,
    _: Annotated[dict, Depends(security.get_current_user)],
) -> list[ServiceMetrics]:
    """Return real-time resource metrics for all containers in a project."""
    if not project_manager.load(project_id):
        raise HTTPException(status_code=404, detail=ERR_PROJECT_NOT_FOUND)
    return [
        _add_metrics_links(m, project_id)
        for m in metrics_service.get_project_metrics(project_id)
    ]
