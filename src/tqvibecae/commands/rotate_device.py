"""Comando — ruota simbolo e ricalcola fili collegati."""

from __future__ import annotations

from typing import Literal
from uuid import UUID

from pydantic import Field

from tqvibecae.commands.base import Command
from tqvibecae.model.presentation import PlacedSymbol, WireSegment
from tqvibecae.model.project import ProjectDocument
from tqvibecae.services.rendering.wire_reroute import (
    apply_wire_segment_updates,
    reroute_wires_for_cp_ids,
)


class RotateDeviceCommand(Command):
    """Aggiorna rotate_deg su PlacedSymbol/Fragment e ricalcola wire."""

    command_type: Literal["rotate_device"] = "rotate_device"
    fragment_id: UUID
    sheet_id: UUID
    device_id: UUID
    old_rotate_deg: float
    new_rotate_deg: float
    cp_positions_before: dict[str, tuple[float, float]] = Field(default_factory=dict)
    cp_positions_after: dict[str, tuple[float, float]] = Field(default_factory=dict)
    wire_segments_before: dict[str, tuple[WireSegment, ...]] = Field(
        default_factory=dict
    )

    def apply(self, document: ProjectDocument) -> None:
        self._set_rotation(document, self.new_rotate_deg)
        self._reroute(document, self.cp_positions_after)

    def revert(self, document: ProjectDocument) -> None:
        self._set_rotation(document, self.old_rotate_deg)
        apply_wire_segment_updates(
            document,
            self.sheet_id,
            {UUID(wid): segs for wid, segs in self.wire_segments_before.items()},
        )

    def _set_rotation(self, document: ProjectDocument, rotate_deg: float) -> None:
        fragment = document.fragments.get(self.fragment_id)
        if fragment is not None:
            sg = fragment.symbol_graphic.model_copy(update={"rotate_deg": rotate_deg})
            document.fragments[self.fragment_id] = fragment.model_copy(
                update={"symbol_graphic": sg}
            )
        presentation = document.presentations.get(self.sheet_id)
        if presentation is None:
            return
        symbols: list[PlacedSymbol] = []
        for placed in presentation.symbols:
            if placed.fragment_id == self.fragment_id:
                symbols.append(placed.model_copy(update={"rotate_deg": rotate_deg}))
            else:
                symbols.append(placed)
        document.presentations[self.sheet_id] = presentation.model_copy(
            update={"symbols": tuple(symbols)}
        )

    def _reroute(
        self,
        document: ProjectDocument,
        cp_positions: dict[str, tuple[float, float]],
    ) -> None:
        positions = {UUID(k): v for k, v in cp_positions.items()}
        presentation = document.presentations.get(self.sheet_id)
        if presentation is None:
            return
        updates = reroute_wires_for_cp_ids(presentation.wires, positions)
        apply_wire_segment_updates(document, self.sheet_id, updates)
