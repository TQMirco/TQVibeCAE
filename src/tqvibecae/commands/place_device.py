"""Comando — posiziona device con fragment e connection points."""

from __future__ import annotations

from typing import Literal
from uuid import UUID

from pydantic import Field

from tqvibecae.commands.base import Command
from tqvibecae.model.catalog_refs import CatalogReference
from tqvibecae.model.device import Device, SchematicFragment, StructuredDesignation
from tqvibecae.model.entity_types import CONNECTION_POINT, DEVICE, SCHEMATIC_FRAGMENT
from tqvibecae.model.presentation import PlacedSymbol, SheetPresentation, SymbolGraphic
from tqvibecae.model.project import ProjectDocument, ProjectIndex
from tqvibecae.model.topology import ConnectionPoint


class PlaceDeviceCommand(Command):
    """Crea Device, SchematicFragment, ConnectionPoint e PlacedSymbol."""

    command_type: Literal["place_device"] = "place_device"
    device_id: UUID
    fragment_id: UUID
    sheet_id: UUID
    composition_ref: CatalogReference
    x_mm: float
    y_mm: float
    rotate_deg: float = 0.0
    designation: str
    connection_points: tuple[tuple[UUID, str], ...] = Field(default_factory=tuple)
    symbol_ref: CatalogReference | None = None

    def apply(self, document: ProjectDocument) -> None:
        device = Device(
            id=self.device_id,
            entity_type=DEVICE,
            designation=StructuredDesignation(component_designator=self.designation),
            component_ref=self.symbol_ref,
        )
        symbol_graphic = SymbolGraphic(
            composition_ref=self.composition_ref,
            x_mm=self.x_mm,
            y_mm=self.y_mm,
            rotate_deg=self.rotate_deg,
        )
        fragment = SchematicFragment(
            id=self.fragment_id,
            entity_type=SCHEMATIC_FRAGMENT,
            device_id=self.device_id,
            sheet_id=self.sheet_id,
            symbol_graphic=symbol_graphic,
        )
        device = device.model_copy(
            update={"schematic_fragment_ids": (self.fragment_id,)}
        )
        document.devices[self.device_id] = device
        document.fragments[self.fragment_id] = fragment

        for cp_id, pin_id in self.connection_points:
            document.connection_points[cp_id] = ConnectionPoint(
                id=cp_id,
                entity_type=CONNECTION_POINT,
                device_id=self.device_id,
                symbol_pin_id=pin_id,
                sheet_id=self.sheet_id,
            )

        presentation = document.presentations.get(self.sheet_id)
        if presentation is None:
            presentation = SheetPresentation(sheet_id=self.sheet_id)
        placed = PlacedSymbol(
            instance_id=self.fragment_id,
            device_id=self.device_id,
            fragment_id=self.fragment_id,
            composition_ref=self.composition_ref,
            x_mm=self.x_mm,
            y_mm=self.y_mm,
            rotate_deg=self.rotate_deg,
            designation=self.designation,
        )
        symbols = (*presentation.symbols, placed)
        document.presentations[self.sheet_id] = presentation.model_copy(
            update={"symbols": symbols}
        )

        sheet_key = str(self.sheet_id)
        device_key = str(self.device_id)
        sheets_for_device = document.index.device_to_sheets.get(device_key, ())
        if sheet_key not in sheets_for_device:
            new_index = dict(document.index.device_to_sheets)
            new_index[device_key] = (*sheets_for_device, sheet_key)
            designation_index = dict(document.index.designation_to_device)
            designation_index[self.designation] = device_key
            document.index = ProjectIndex(
                device_to_sheets=new_index,
                designation_to_device=designation_index,
                net_to_devices=dict(document.index.net_to_devices),
            )

    def revert(self, document: ProjectDocument) -> None:
        document.devices.pop(self.device_id, None)
        document.fragments.pop(self.fragment_id, None)
        for cp_id, _ in self.connection_points:
            document.connection_points.pop(cp_id, None)

        presentation = document.presentations.get(self.sheet_id)
        if presentation is not None:
            symbols = tuple(
                s for s in presentation.symbols if s.fragment_id != self.fragment_id
            )
            document.presentations[self.sheet_id] = presentation.model_copy(
                update={"symbols": symbols}
            )

        device_key = str(self.device_id)
        sheet_key = str(self.sheet_id)
        new_device_sheets = dict(document.index.device_to_sheets)
        remaining = tuple(
            s for s in new_device_sheets.get(device_key, ()) if s != sheet_key
        )
        if remaining:
            new_device_sheets[device_key] = remaining
        else:
            new_device_sheets.pop(device_key, None)
        new_designations = {
            k: v
            for k, v in document.index.designation_to_device.items()
            if v != device_key
        }
        document.index = ProjectIndex(
            device_to_sheets=new_device_sheets,
            designation_to_device=new_designations,
            net_to_devices=dict(document.index.net_to_devices),
        )
