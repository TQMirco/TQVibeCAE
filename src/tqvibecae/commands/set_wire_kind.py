"""Comando — aggiorna tipo visivo filo (presentation)."""

from __future__ import annotations

from typing import Literal
from uuid import UUID

from tqvibecae.commands.base import Command
from tqvibecae.model.presentation import WireKind
from tqvibecae.model.project import ProjectDocument


class SetWireKindCommand(Command):
    """Aggiorna WireKind su WireGraphic."""

    command_type: Literal["set_wire_kind"] = "set_wire_kind"
    wire_id: UUID
    sheet_id: UUID
    new_kind: WireKind
    old_kind: WireKind

    def apply(self, document: ProjectDocument) -> None:
        self._set_kind(document, self.new_kind)

    def revert(self, document: ProjectDocument) -> None:
        self._set_kind(document, self.old_kind)

    def _set_kind(self, document: ProjectDocument, kind: WireKind) -> None:
        presentation = document.presentations.get(self.sheet_id)
        if presentation is None:
            return
        wires = tuple(
            w.model_copy(update={"wire_kind": kind}) if w.wire_id == self.wire_id else w
            for w in presentation.wires
        )
        document.presentations[self.sheet_id] = presentation.model_copy(
            update={"wires": wires}
        )
