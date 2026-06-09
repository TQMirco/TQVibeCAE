"""Composizioni grafiche da celle base."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from tqvibecae.model.base import Entity
from tqvibecae.model.entity_types import SYMBOL_GRAPHIC_COMPOSITION
from tqvibecae.model.graphics.cells import GraphicCellInstance


class PinMapping(BaseModel):
    """Mappa anchor cella → pin logico simbolo."""

    model_config = ConfigDict(frozen=True)

    symbol_pin_id: str
    cell_instance_id: str
    cell_anchor_id: str


class SymbolGraphicComposition(Entity):
    """Composizione di celle — es. interruttore 3 poli = 3x contatto."""

    entity_type: str = SYMBOL_GRAPHIC_COMPOSITION
    name: str
    cells: tuple[GraphicCellInstance, ...]
    pin_map: tuple[PinMapping, ...] = ()
