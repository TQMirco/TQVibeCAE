"""Progetto, fogli e indice denormalizzato."""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from tqvibecae.model.base import Entity, ProjectLocaleProfile
from tqvibecae.model.entity_types import PROJECT, SHEET
from tqvibecae.model.presentation import SheetPresentation
from tqvibecae.model.settings import ProjectSettings
from tqvibecae.model.topology import Cable, ConnectionPoint, Net

if TYPE_CHECKING:
    from tqvibecae.model.device import Device, SchematicFragment


class ProjectIndex(BaseModel):
    """Indice denormalizzato per ricerche O(1)."""

    model_config = ConfigDict(frozen=True)

    device_to_sheets: dict[str, tuple[str, ...]] = Field(default_factory=dict)
    designation_to_device: dict[str, str] = Field(default_factory=dict)
    net_to_devices: dict[str, tuple[str, ...]] = Field(default_factory=dict)


class Sheet(Entity):
    """Foglio schema elettrico."""

    entity_type: str = SHEET
    title: str
    revision_label: str = "A"


class Project(Entity):
    """Root documento progetto."""

    entity_type: str = PROJECT
    schema_version: int = Field(default=1, ge=1)
    name: str
    settings: ProjectSettings = Field(default_factory=ProjectSettings)
    locale: ProjectLocaleProfile = Field(
        default_factory=lambda: ProjectLocaleProfile(document_languages=("it",))
    )
    sheet_ids: tuple[str, ...] = Field(default_factory=tuple)


class ProjectDocument(BaseModel):
    """Stato progetto in memoria — container per CommandBus."""

    project: Project
    sheets: dict[UUID, Sheet] = Field(default_factory=dict)
    devices: dict[UUID, Device] = Field(default_factory=dict)
    fragments: dict[UUID, SchematicFragment] = Field(default_factory=dict)
    connection_points: dict[UUID, ConnectionPoint] = Field(default_factory=dict)
    nets: dict[UUID, Net] = Field(default_factory=dict)
    cables: dict[UUID, Cable] = Field(default_factory=dict)
    presentations: dict[UUID, SheetPresentation] = Field(default_factory=dict)
    index: ProjectIndex = Field(default_factory=ProjectIndex)
    active_sheet_id: UUID | None = None


from tqvibecae.model.device import Device, SchematicFragment  # noqa: E402

ProjectDocument.model_rebuild()
