"""Definizioni catalogo libreria versionate."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from tqvibecae.model.base import Entity, LocalizedString
from tqvibecae.model.catalog_refs import CatalogReference
from tqvibecae.model.entity_types import (
    COMPONENT_DEFINITION,
    FOOTPRINT_DEFINITION,
    PART_NUMBER,
    SYMBOL_DEFINITION,
)
from tqvibecae.model.media import MediaAttachmentRef


class ConnectionPointTemplate(BaseModel):
    """Template pin logico su SymbolDefinition."""

    model_config = ConfigDict(frozen=True)

    pin_id: str
    label: str | None = None
    direction_deg: float | None = None


class SymbolDefinition(Entity):
    """Funzione elettrica IEC con riferimento grafica componibile."""

    entity_type: str = SYMBOL_DEFINITION
    function_class: str
    graphic_composition_ref: CatalogReference
    connection_points_template: tuple[ConnectionPointTemplate, ...] = Field(
        default_factory=tuple
    )
    norm: str = "IEC 60617"


class ComponentDefinition(Entity):
    """Caratteristiche tecniche categoria componente."""

    entity_type: str = COMPONENT_DEFINITION
    name: LocalizedString
    category: str
    symbol_ref: CatalogReference | None = None
    auxiliary_slots: int = Field(default=0, ge=0)
    contact_block_slots: int = Field(default=0, ge=0)
    compatible_subpart_ids: tuple[UUID, ...] = Field(default_factory=tuple)
    media: tuple[MediaAttachmentRef, ...] = Field(default_factory=tuple)


class PartNumber(Entity):
    """Prodotto commerciale costruttore."""

    entity_type: str = PART_NUMBER
    manufacturer: str
    order_number: str
    component_ref: CatalogReference
    description: LocalizedString | None = None
    media: tuple[MediaAttachmentRef, ...] = Field(default_factory=tuple)


class FootprintDefinition(Entity):
    """Ingombro fisico layout quadro."""

    entity_type: str = FOOTPRINT_DEFINITION
    name: str
    width_mm: float = Field(gt=0.0)
    height_mm: float = Field(gt=0.0)
    din_modules: float = Field(default=1.0, gt=0.0)
    component_ref: CatalogReference | None = None
