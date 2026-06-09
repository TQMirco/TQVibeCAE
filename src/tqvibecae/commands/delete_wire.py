"""Comando — elimina filo presentation e net 2-pin."""

from __future__ import annotations

from typing import Literal
from uuid import UUID

from tqvibecae.commands.base import Command
from tqvibecae.model.presentation import WireGraphic
from tqvibecae.model.project import ProjectDocument, ProjectIndex
from tqvibecae.model.topology import Net


class DeleteWireCommand(Command):
    """Rimuove WireGraphic; se net ha 2 CP rimuove anche la net."""

    command_type: Literal["delete_wire"] = "delete_wire"
    wire_id: UUID
    sheet_id: UUID
    saved_wire: WireGraphic | None = None
    saved_net: Net | None = None
    saved_index: ProjectIndex | None = None

    def apply(self, document: ProjectDocument) -> None:
        self.saved_index = document.index
        presentation = document.presentations.get(self.sheet_id)
        if presentation is None:
            return
        remaining: list[WireGraphic] = []
        for wire in presentation.wires:
            if wire.wire_id == self.wire_id:
                self.saved_wire = wire
            else:
                remaining.append(wire)
        document.presentations[self.sheet_id] = presentation.model_copy(
            update={"wires": tuple(remaining)}
        )
        if self.saved_wire is not None and self.saved_wire.net_id is not None:
            net = document.nets.get(self.saved_wire.net_id)
            if net is not None and len(net.connection_point_ids) == 2:
                self.saved_net = net
                document.nets.pop(net.id, None)
                net_index = dict(document.index.net_to_devices)
                net_index.pop(str(net.id), None)
                document.index = ProjectIndex(
                    device_to_sheets=dict(document.index.device_to_sheets),
                    designation_to_device=dict(document.index.designation_to_device),
                    net_to_devices=net_index,
                )

    def revert(self, document: ProjectDocument) -> None:
        presentation = document.presentations.get(self.sheet_id)
        if presentation is not None and self.saved_wire is not None:
            document.presentations[self.sheet_id] = presentation.model_copy(
                update={"wires": (*presentation.wires, self.saved_wire)}
            )
        if self.saved_net is not None:
            document.nets[self.saved_net.id] = self.saved_net
        if self.saved_index is not None:
            document.index = self.saved_index
