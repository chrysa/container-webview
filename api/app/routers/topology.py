from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.constants import ERR_PROJECT_NOT_FOUND
from app.security import security
from app.services.topology_service import TopologyGraph, topology_service

router = APIRouter()

_NOT_FOUND = {404: {"description": ERR_PROJECT_NOT_FOUND}}


@router.get("/{project_id}/topology", responses=_NOT_FOUND)
def get_topology(
    project_id: str, _: Annotated[dict, Depends(security.get_current_user)]
) -> TopologyGraph:
    """Return the topology graph for a Compose project."""
    graph = topology_service.build(project_id)
    if graph is None:
        raise HTTPException(status_code=404, detail=ERR_PROJECT_NOT_FOUND)
    return graph
