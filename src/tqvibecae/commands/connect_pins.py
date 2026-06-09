"""Comando — collega pin in Net e aggiunge WireGraphic."""

from __future__ import annotations

from typing import Literal
from uuid import UUID

from pydantic import Field

from tqvibecae.commands.base import Command
from tqvibecae.model.entity_types import NET
from tqvibecae.model.presentation import (
    SheetPresentation,
    WireGraphic,
    WireKind,
    WireSegment,
    pin_ref,
)
from tqvibecae.model.project import ProjectDocument, ProjectIndex
from tqvibecae.model.topology import Net


class ConnectPinsCommand(Command):
    """Unisce connection point in una Net e disegna filo presentation."""

    command_type: Literal["connect_pins"] = "connect_pins"
    wire_id: UUID
    net_id: UUID
    sheet_id: UUID
    from_cp_id: UUID
    to_cp_id: UUID
    wire_kind: WireKind = WireKind.CONTROL
    segments: tuple[WireSegment, ...] = Field(default_factory=tuple)
    merged_net_ids: tuple[UUID, ...] = Field(default_factory=tuple)
    removed_nets: tuple[Net, ...] = Field(default_factory=tuple)
    previous_net_id_from: UUID | None = None
    previous_net_id_to: UUID | None = None

    def apply(self, document: ProjectDocument) -> None:
        cp_ids = self._collect_connection_points(document)
        document.nets[self.net_id] = Net(
            id=self.net_id,
            entity_type=NET,
            connection_point_ids=cp_ids,
        )
        for old_id in self.merged_net_ids:
            if old_id != self.net_id:
                document.nets.pop(old_id, None)

        wire = WireGraphic(
            wire_id=self.wire_id,
            segments=self.segments,
            wire_kind=self.wire_kind,
            from_pin_ref=pin_ref(self.from_cp_id),
            to_pin_ref=pin_ref(self.to_cp_id),
            net_id=self.net_id,
        )
        presentation = document.presentations.get(self.sheet_id)
        if presentation is None:
            presentation = SheetPresentation(sheet_id=self.sheet_id)
        wires = (*presentation.wires, wire)
        document.presentations[self.sheet_id] = presentation.model_copy(
            update={"wires": wires}
        )
        self._update_net_index(document, cp_ids)

    def revert(self, document: ProjectDocument) -> None:
        document.nets.pop(self.net_id, None)
        for net in self.removed_nets:
            if net.id != self.net_id:
                document.nets[net.id] = net

        presentation = document.presentations.get(self.sheet_id)
        if presentation is not None:
            wires = tuple(w for w in presentation.wires if w.wire_id != self.wire_id)
            document.presentations[self.sheet_id] = presentation.model_copy(
                update={"wires": wires}
            )

    def _collect_connection_points(self, document: ProjectDocument) -> tuple[UUID, ...]:
        collected: set[UUID] = {self.from_cp_id, self.to_cp_id}
        for net in document.nets.values():
            if self.from_cp_id in net.connection_point_ids:
                collected.update(net.connection_point_ids)
            if self.to_cp_id in net.connection_point_ids:
                collected.update(net.connection_point_ids)
        for merged_id in self.merged_net_ids:
            net = document.nets.get(merged_id)
            if net is not None:
                collected.update(net.connection_point_ids)
        return tuple(sorted(collected, key=str))

    def _net_cp_ids_before(
        self, document: ProjectDocument, cp_id: UUID
    ) -> tuple[UUID, ...]:
        for net in document.nets.values():
            if cp_id in net.connection_point_ids and net.id != self.net_id:
                return net.connection_point_ids
        return (cp_id,)

    def _update_net_index(
        self, document: ProjectDocument, cp_ids: tuple[UUID, ...]
    ) -> None:
        device_ids: set[str] = set()
        for cp_id in cp_ids:
            cp = document.connection_points.get(cp_id)
            if cp is not None and cp.device_id is not None:
                device_ids.add(str(cp.device_id))
        net_index = dict(document.index.net_to_devices)
        net_index[str(self.net_id)] = tuple(sorted(device_ids))
        document.index = ProjectIndex(
            device_to_sheets=dict(document.index.device_to_sheets),
            designation_to_device=dict(document.index.designation_to_device),
            net_to_devices=net_index,
        )
