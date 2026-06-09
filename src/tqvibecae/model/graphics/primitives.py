"""Primitive grafiche e trasformazioni."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

PrimitiveType = Literal["line", "polyline", "arc", "circle", "rect", "text"]


class GraphicPrimitive(BaseModel):
    """Atomo di disegno con coordinate normalizzate 0..1 nella cella."""

    model_config = ConfigDict(frozen=True)

    primitive_type: PrimitiveType
    geometry: dict[str, float | tuple[float, ...]]
    stroke_width: float = 1.0
    layer: str = "symbol"


class GraphicTransform(BaseModel):
    """Trasformazione locale di un'istanza cella."""

    model_config = ConfigDict(frozen=True)

    translate_x_mm: float = 0.0
    translate_y_mm: float = 0.0
    rotate_deg: float = 0.0
    scale: float = Field(default=1.0, gt=0.0)


class PinAnchor(BaseModel):
    """Punto di connessione elettrica sulla cella (coordinate normalizzate)."""

    model_config = ConfigDict(frozen=True)

    anchor_id: str
    x: float
    y: float
    direction_deg: float | None = None
