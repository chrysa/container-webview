from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from app.constants import API_V1_PREFIX
from app.constants import ERR_PROJECT_NOT_FOUND
from app.models.hateoas import HateoasLink
from app.models.hateoas import TopologyLinks
from app.security import security
from app.services.topology_service import TopologyGraph
from app.services.topology_service import topology_service

router = APIRouter()

_NOT_FOUND = {404: {"description": ERR_PROJECT_NOT_FOUND}}


def _add_topology_links(graph: TopologyGraph, project_id: str) -> TopologyGraph:
    """Attach HATEOAS navigation links to a TopologyGraph instance."""
    graph.links = TopologyLinks(
        self=HateoasLink(href=f"{API_V1_PREFIX}/projects/{project_id}/topology"),
        project=HateoasLink(href=f"{API_V1_PREFIX}/projects/{project_id}"),
        metrics=HateoasLink(href=f"{API_V1_PREFIX}/projects/{project_id}/metrics"),
    )
    return graph


@router.get("/{project_id}/topology", responses=_NOT_FOUND)
def get_topology(
    project_id: str, _: Annotated[dict, Depends(security.get_current_user)]
) -> TopologyGraph:
    """Return the topology graph for a Compose project."""
    graph = topology_service.build(project_id)
    if graph is None:
        raise HTTPException(status_code=404, detail=ERR_PROJECT_NOT_FOUND)
    return _add_topology_links(graph, project_id)
