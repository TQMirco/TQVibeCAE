"""Device e fragment schematici."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from tqvibecae.model.base import Entity
from tqvibecae.model.catalog_refs import CatalogReference
from tqvibecae.model.entity_types import DEVICE, SCHEMATIC_FRAGMENT, SUB_COMPONENT
from tqvibecae.model.media import MediaAttachmentRef
from tqvibecae.model.presentation import SymbolGraphic


class StructuredDesignation(BaseModel):
    """Designazione IEC 81346 — componente, locazione, funzione."""

    model_config = ConfigDict(frozen=True)

    function_prefix: str | None = None
    location_prefix: str | None = None
    component_designator: str


class SubComponent(Entity):
    """Parte fisica decomposta (blocco ausiliario, testa pulsante, ...)."""

    entity_type: str = SUB_COMPONENT
    parent_device_id: UUID
    component_ref: CatalogReference | None = None
    part_ref: CatalogReference | None = None


class Device(Entity):
    """Identità canonica di un componente fisico nel progetto."""

    entity_type: str = DEVICE
    designation: StructuredDesignation
    component_ref: CatalogReference | None = None
    part_ref: CatalogReference | None = None
    sub_components: tuple[SubComponent, ...] = Field(default_factory=tuple)
    schematic_fragment_ids: tuple[UUID, ...] = Field(default_factory=tuple)
    layout_placement_id: UUID | None = None
    media: tuple[MediaAttachmentRef, ...] = Field(default_factory=tuple)


class SchematicFragment(Entity):
    """Apparizione grafica di un device su un foglio."""

    entity_type: str = SCHEMATIC_FRAGMENT
    device_id: UUID
    sheet_id: UUID
    symbol_graphic: SymbolGraphic
