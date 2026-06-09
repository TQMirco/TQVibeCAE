"""Comando — elimina device, wire collegati e net orfane."""

from __future__ import annotations

from typing import Literal
from uuid import UUID

from pydantic import Field

from tqvibecae.commands.base import Command
from tqvibecae.model.device import Device, SchematicFragment
from tqvibecae.model.presentation import PlacedSymbol, SheetPresentation, WireGraphic
from tqvibecae.model.project import ProjectDocument, ProjectIndex
from tqvibecae.model.topology import ConnectionPoint, Net
from tqvibecae.services.rendering.wire_reroute import wire_touches_cp


class DeleteDeviceCommand(Command):
    """Rimuove device, fragment, CP, wire e aggiorna net/index."""

    command_type: Literal["delete_device"] = "delete_device"
    device_id: UUID
    fragment_id: UUID
    sheet_id: UUID
    saved_device: Device | None = None
    saved_fragment: SchematicFragment | None = None
    saved_connection_points: tuple[ConnectionPoint, ...] = Field(default_factory=tuple)
    saved_placed_symbol: PlacedSymbol | None = None
    saved_wires: tuple[WireGraphic, ...] = Field(default_factory=tuple)
    saved_nets: tuple[Net, ...] = Field(default_factory=tuple)
    saved_index: ProjectIndex | None = None

    def apply(self, document: ProjectDocument) -> None:
        self.saved_index = document.index
        device = document.devices.pop(self.device_id, None)
        if device is not None:
            self.saved_device = device
        fragment = document.fragments.pop(self.fragment_id, None)
        if fragment is not None:
            self.saved_fragment = fragment

        cp_ids: list[UUID] = []
        saved_cps: list[ConnectionPoint] = []
        for cp_id, cp in list(document.connection_points.items()):
            if cp.device_id == self.device_id:
                cp_ids.append(cp_id)
                saved_cps.append(cp)
                document.connection_points.pop(cp_id, None)
        self.saved_connection_points = tuple(saved_cps)

        presentation = document.presentations.get(self.sheet_id)
        if presentation is not None:
            for placed in presentation.symbols:
                if placed.fragment_id == self.fragment_id:
                    self.saved_placed_symbol = placed
                    break
            remaining_wires: list[WireGraphic] = []
            removed_wires: list[WireGraphic] = []
            for wire in presentation.wires:
                if any(wire_touches_cp(wire, cp_id) for cp_id in cp_ids):
                    removed_wires.append(wire)
                else:
                    remaining_wires.append(wire)
            self.saved_wires = tuple(removed_wires)
            symbols = tuple(
                s for s in presentation.symbols if s.fragment_id != self.fragment_id
            )
            document.presentations[self.sheet_id] = presentation.model_copy(
                update={"symbols": symbols, "wires": tuple(remaining_wires)}
            )

        saved_nets: list[Net] = []
        for net_id, net in list(document.nets.items()):
            remaining = tuple(cp for cp in net.connection_point_ids if cp not in cp_ids)
            if len(remaining) != len(net.connection_point_ids):
                saved_nets.append(net)
                if len(remaining) < 2:
                    document.nets.pop(net_id, None)
                else:
                    document.nets[net_id] = net.model_copy(
                        update={"connection_point_ids": remaining}
                    )
        self.saved_nets = tuple(saved_nets)

        device_key = str(self.device_id)
        sheet_key = str(self.sheet_id)
        new_device_sheets = dict(document.index.device_to_sheets)
        remaining_sheets = tuple(
            s for s in new_device_sheets.get(device_key, ()) if s != sheet_key
        )
        if remaining_sheets:
            new_device_sheets[device_key] = remaining_sheets
        else:
            new_device_sheets.pop(device_key, None)
        old_designation = None
        if self.saved_device is not None:
            old_designation = self.saved_device.designation.component_designator
        new_designations = dict(document.index.designation_to_device)
        if old_designation:
            new_designations.pop(old_designation, None)
        net_index = {
            k: v for k, v in document.index.net_to_devices.items() if k in document.nets
        }
        document.index = ProjectIndex(
            device_to_sheets=new_device_sheets,
            designation_to_device=new_designations,
            net_to_devices=net_index,
        )

    def revert(self, document: ProjectDocument) -> None:
        if self.saved_device is not None:
            document.devices[self.device_id] = self.saved_device
        if self.saved_fragment is not None:
            document.fragments[self.fragment_id] = self.saved_fragment
        for cp in self.saved_connection_points:
            document.connection_points[cp.id] = cp
        for net in self.saved_nets:
            document.nets[net.id] = net
        presentation = document.presentations.get(self.sheet_id)
        if presentation is None:
            presentation = SheetPresentation(sheet_id=self.sheet_id)
        symbols = presentation.symbols
        if self.saved_placed_symbol is not None:
            symbols = (*symbols, self.saved_placed_symbol)
        wires = (*presentation.wires, *self.saved_wires)
        document.presentations[self.sheet_id] = presentation.model_copy(
            update={"symbols": symbols, "wires": wires}
        )
        if self.saved_index is not None:
            document.index = self.saved_index
