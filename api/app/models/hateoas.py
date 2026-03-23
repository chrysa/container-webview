"""HATEOAS link models shared across all routers."""

from pydantic import BaseModel


class HateoasLink(BaseModel):
    """A single HATEOAS hyperlink."""

    href: str


class ProjectLinks(BaseModel):
    """Links embedded in a ProjectModel response."""

    self: HateoasLink
    topology: HateoasLink
    metrics: HateoasLink
    alerts: HateoasLink


class AlertLinks(BaseModel):
    """Links embedded in an Alert response."""

    self: HateoasLink
    project: HateoasLink


class TopologyLinks(BaseModel):
    """Links embedded in a topology response."""

    self: HateoasLink
    project: HateoasLink
    metrics: HateoasLink


class MetricsLinks(BaseModel):
    """Links embedded in a metrics response."""

    self: HateoasLink
    project: HateoasLink
