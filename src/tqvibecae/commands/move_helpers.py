"""Helper costruzione comandi move/rotate con reroute wire."""

from __future__ import annotations

from uuid import UUID

from tqvibecae.commands.move_device import MoveDeviceCommand
from tqvibecae.commands.rotate_device import RotateDeviceCommand
from tqvibecae.model.presentation import PlacedSymbol
from tqvibecae.model.project import ProjectDocument
from tqvibecae.services.rendering.graphic_resolver import (
    InMemoryGraphicLibrary,
    resolve_placed_symbol,
)


def _cp_positions_for_device(
    document: ProjectDocument,
    library: InMemoryGraphicLibrary,
    placed: PlacedSymbol,
) -> dict[str, tuple[float, float]]:
    graphic = resolve_placed_symbol(library, placed)
    composition = library.get_composition(placed.composition_ref)
    cp_by_pin: dict[str, UUID] = {}
    for cp_id, cp in document.connection_points.items():
        if cp.device_id == placed.device_id and cp.symbol_pin_id:
            cp_by_pin[cp.symbol_pin_id] = cp_id
    positions: dict[str, tuple[float, float]] = {}
    for mapping in composition.pin_map:
        cp_id = cp_by_pin.get(mapping.symbol_pin_id)
        if cp_id is None:
            continue
        for pin in graphic.pin_anchors:
            if pin.symbol_pin_id == mapping.symbol_pin_id:
                positions[str(cp_id)] = (pin.x_mm, pin.y_mm)
                break
    return positions


def build_move_device_command(
    document: ProjectDocument,
    library: InMemoryGraphicLibrary,
    placed: PlacedSymbol,
    new_x_mm: float,
    new_y_mm: float,
) -> MoveDeviceCommand:
    """Costruisce MoveDeviceCommand con snapshot wire e posizioni pin."""
    fragment = document.fragments.get(placed.fragment_id)
    if fragment is None:
        msg = "Fragment not found for move command"
        raise ValueError(msg)
    sheet_id = fragment.sheet_id

    cp_before = _cp_positions_for_device(document, library, placed)
    moved = placed.model_copy(update={"x_mm": new_x_mm, "y_mm": new_y_mm})
    cp_after = _cp_positions_for_device(document, library, moved)
    presentation = document.presentations.get(sheet_id)
    wire_before: dict[str, tuple] = {}
    if presentation is not None:
        wire_before = {str(w.wire_id): w.segments for w in presentation.wires}

    return MoveDeviceCommand(
        fragment_id=placed.fragment_id,
        sheet_id=sheet_id,
        device_id=placed.device_id,
        old_x_mm=placed.x_mm,
        old_y_mm=placed.y_mm,
        new_x_mm=new_x_mm,
        new_y_mm=new_y_mm,
        cp_positions_before=cp_before,
        cp_positions_after=cp_after,
        wire_segments_before=wire_before,
    )


def build_rotate_device_command(
    document: ProjectDocument,
    library: InMemoryGraphicLibrary,
    placed: PlacedSymbol,
    new_rotate_deg: float,
) -> RotateDeviceCommand:
    """Costruisce RotateDeviceCommand con snapshot wire e posizioni pin."""
    fragment = document.fragments.get(placed.fragment_id)
    if fragment is None:
        msg = "Fragment not found for rotate command"
        raise ValueError(msg)
    sheet_id = fragment.sheet_id

    cp_before = _cp_positions_for_device(document, library, placed)
    rotated = placed.model_copy(update={"rotate_deg": new_rotate_deg})
    cp_after = _cp_positions_for_device(document, library, rotated)
    presentation = document.presentations.get(sheet_id)
    wire_before: dict[str, tuple] = {}
    if presentation is not None:
        wire_before = {str(w.wire_id): w.segments for w in presentation.wires}

    return RotateDeviceCommand(
        fragment_id=placed.fragment_id,
        sheet_id=sheet_id,
        device_id=placed.device_id,
        old_rotate_deg=placed.rotate_deg,
        new_rotate_deg=new_rotate_deg,
        cp_positions_before=cp_before,
        cp_positions_after=cp_after,
        wire_segments_before=wire_before,
    )
