"""Celle grafiche base riusabili."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, model_validator

from tqvibecae.model.base import Entity
from tqvibecae.model.catalog_refs import CatalogReference
from tqvibecae.model.entity_types import GRAPHIC_CELL
from tqvibecae.model.graphics.primitives import (
    GraphicPrimitive,
    GraphicTransform,
    PinAnchor,
)


class GraphicCellDefinition(Entity):
    """Elemento grafico standard riusabile — es. un contatto NA IEC."""

    entity_type: str = GRAPHIC_CELL
    name: str
    category: str
    primitives: tuple[GraphicPrimitive, ...]
    pin_anchors: tuple[PinAnchor, ...]
    width_mm: float = Field(gt=0.0)
    height_mm: float = Field(gt=0.0)


class GraphicCellInstance(BaseModel):
    """Istanza di una cella base con transform e ripetizione."""

    model_config = ConfigDict(frozen=True)

    cell_ref: CatalogReference
    instance_id: str
    transform: GraphicTransform = Field(default_factory=GraphicTransform)
    repeat_count: int = Field(default=1, ge=1)
    repeat_spacing_mm: float | None = None

    @model_validator(mode="after")
    def _validate_repeat_spacing(self) -> GraphicCellInstance:
        if self.repeat_count > 1 and self.repeat_spacing_mm is None:
            msg = "repeat_spacing_mm is required when repeat_count > 1"
            raise ValueError(msg)
        return self
