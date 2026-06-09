"""Routing ortogonale fili presentation."""

from __future__ import annotations

from typing import Literal

from beartype import beartype

from tqvibecae.model.presentation import WireSegment

Point2D = tuple[float, float]
BendMode = Literal["hv", "vh"]


@beartype
def _snap(value: float, snap_mm: float | None) -> float:
    if snap_mm is None or snap_mm <= 0:
        return value
    return round(value / snap_mm) * snap_mm


@beartype
def route_orthogonal(
    start: Point2D,
    end: Point2D,
    *,
    bend: BendMode = "hv",
    snap_mm: float | None = None,
) -> tuple[WireSegment, ...]:
    """Manhattan: 1 segmento se allineati, altrimenti 2 segmenti ortogonali."""
    x1, y1 = start
    x2, y2 = end
    if snap_mm is not None:
        x2 = _snap(x2, snap_mm)
        y2 = _snap(y2, snap_mm)
    if abs(x1 - x2) < 1e-9 or abs(y1 - y2) < 1e-9:
        return (WireSegment(x1_mm=x1, y1_mm=y1, x2_mm=x2, y2_mm=y2),)
    mid_x = _snap(x2, snap_mm) if bend == "hv" else x1
    mid_y = y1 if bend == "hv" else _snap(y2, snap_mm)
    mid = (mid_x, mid_y)
    return (
        WireSegment(x1_mm=x1, y1_mm=y1, x2_mm=mid[0], y2_mm=mid[1]),
        WireSegment(x1_mm=mid[0], y1_mm=mid[1], x2_mm=x2, y2_mm=y2),
    )
