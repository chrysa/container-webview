from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends

from app.constants import API_V1_PREFIX
from app.models.hateoas import AlertLinks
from app.models.hateoas import HateoasLink
from app.security import security
from app.services.alerts_service import Alert
from app.services.alerts_service import alerts_service

router = APIRouter()


def _add_alert_links(alert: Alert) -> Alert:
    """Attach HATEOAS navigation links to an Alert instance."""
    alert.links = AlertLinks(
        self=HateoasLink(href=f"{API_V1_PREFIX}/alerts/project/{alert.project}"),
        project=HateoasLink(href=f"{API_V1_PREFIX}/projects/{alert.project}"),
    )
    return alert


@router.get("")
def get_alerts(
    _: Annotated[dict, Depends(security.get_current_user)]
) -> list[Alert]:
    """Return all operational alerts across every running container."""
    return [_add_alert_links(a) for a in alerts_service.get_all()]


@router.get("/project/{project_id}")
def get_project_alerts(
    project_id: str,
    _: Annotated[dict, Depends(security.get_current_user)],
) -> list[Alert]:
    """Return alerts filtered to a specific Compose project."""
    return [_add_alert_links(a) for a in alerts_service.get_for_project(project_id)]
