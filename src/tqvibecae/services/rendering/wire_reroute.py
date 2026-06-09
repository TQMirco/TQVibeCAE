"""Ricalcolo segmenti fili dopo spostamento/rotazione simboli."""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from tqvibecae.model.presentation import WireGraphic, WireSegment, pin_ref
from tqvibecae.model.project import ProjectDocument
from tqvibecae.services.rendering.wire_router import route_orthogonal

if TYPE_CHECKING:
    from tqvibecae.viewmodel.schematic_editor_vm import PinHit

Point2D = tuple[float, float]


def cp_positions_from_pin_hits(
    pin_hits: tuple[PinHit, ...],
) -> dict[UUID, Point2D]:
    """Mappa connection_point_id -> posizione mm da PinHit-like objects."""
    positions: dict[UUID, Point2D] = {}
    for hit in pin_hits:
        positions[hit.connection_point_id] = (hit.x_mm, hit.y_mm)
    return positions


def reroute_wires_for_cp_ids(
    wires: tuple[WireGraphic, ...],
    cp_positions: dict[UUID, Point2D],
    *,
    snap_mm: float | None = None,
) -> dict[UUID, tuple[WireSegment, ...]]:
    """Ricalcola segmenti per fili i cui estremi sono in cp_positions."""
    updated: dict[UUID, tuple[WireSegment, ...]] = {}
    for wire in wires:
        try:
            from_cp = UUID(wire.from_pin_ref)
            to_cp = UUID(wire.to_pin_ref)
        except ValueError:
            continue
        start = cp_positions.get(from_cp)
        end = cp_positions.get(to_cp)
        if start is None or end is None:
            continue
        updated[wire.wire_id] = route_orthogonal(
            start,
            end,
            snap_mm=snap_mm,
        )
    return updated


def apply_wire_segment_updates(
    document: ProjectDocument,
    sheet_id: UUID,
    updates: dict[UUID, tuple[WireSegment, ...]],
) -> None:
    """Applica nuovi segmenti ai WireGraphic del foglio."""
    presentation = document.presentations.get(sheet_id)
    if presentation is None:
        return
    new_wires: list[WireGraphic] = []
    for wire in presentation.wires:
        segments = updates.get(wire.wire_id)
        if segments is not None:
            new_wires.append(wire.model_copy(update={"segments": segments}))
        else:
            new_wires.append(wire)
    document.presentations[sheet_id] = presentation.model_copy(
        update={"wires": tuple(new_wires)}
    )


def wire_touches_cp(wire: WireGraphic, cp_id: UUID) -> bool:
    """True se il filo collega il connection point."""
    return wire.from_pin_ref == pin_ref(cp_id) or wire.to_pin_ref == pin_ref(cp_id)
