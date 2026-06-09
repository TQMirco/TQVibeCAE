"""Presentation layer — posizione grafica su foglio e fili canvas."""

from __future__ import annotations

from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from tqvibecae.model.catalog_refs import CatalogReference


class WireKind(StrEnum):
    """Tipo visivo conduttore su canvas."""

    CONTROL = "control"
    POWER = "power"
    PE = "pe"


class SymbolGraphic(BaseModel):
    """Istanza presentation di una composizione su canvas."""

    model_config = ConfigDict(frozen=True)

    composition_ref: CatalogReference
    x_mm: float = 0.0
    y_mm: float = 0.0
    rotate_deg: float = Field(default=0.0)


class WireSegment(BaseModel):
    """Segmento ortogonale di un filo (mm)."""

    model_config = ConfigDict(frozen=True)

    x1_mm: float
    y1_mm: float
    x2_mm: float
    y2_mm: float


class WireGraphic(BaseModel):
    """Conduttore presentation — disegno canvas, non topologia Net."""

    model_config = ConfigDict(frozen=True)

    wire_id: UUID
    segments: tuple[WireSegment, ...]
    wire_kind: WireKind = WireKind.CONTROL
    from_pin_ref: str
    to_pin_ref: str
    net_id: UUID | None = None


class PlacedSymbol(BaseModel):
    """Simbolo posizionato sul foglio con link al dominio."""

    model_config = ConfigDict(frozen=True)

    instance_id: UUID
    device_id: UUID
    fragment_id: UUID
    composition_ref: CatalogReference
    x_mm: float = 0.0
    y_mm: float = 0.0
    rotate_deg: float = 0.0
    designation: str | None = None


class SheetPresentation(BaseModel):
    """Stato grafico di un foglio per rendering canvas."""

    sheet_id: UUID
    symbols: tuple[PlacedSymbol, ...] = Field(default_factory=tuple)
    wires: tuple[WireGraphic, ...] = Field(default_factory=tuple)
    grid_mm: float = Field(default=10.0, gt=0.0)


def pin_ref(connection_point_id: UUID) -> str:
    """Riferimento stabile pin per wire tool."""
    return str(connection_point_id)
