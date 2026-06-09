"""Test comandi editing — move, delete, wire kind."""

from __future__ import annotations

from uuid import uuid4

from tqvibecae.commands.command_bus import CommandBus
from tqvibecae.commands.connect_helpers import build_connect_pins_command
from tqvibecae.commands.delete_device import DeleteDeviceCommand
from tqvibecae.commands.delete_wire import DeleteWireCommand
from tqvibecae.commands.move_helpers import build_move_device_command
from tqvibecae.commands.place_device import PlaceDeviceCommand
from tqvibecae.commands.project_factory import create_empty_project
from tqvibecae.commands.set_wire_kind import SetWireKindCommand
from tqvibecae.model.presentation import WireKind, WireSegment
from tqvibecae.model.settings import ApplicationSettings
from tqvibecae.resources.iec_catalog.catalog import build_standard_catalog
from tqvibecae.services.rendering.wire_router import route_orthogonal


def _place_single_contact(bus: CommandBus) -> tuple:
    catalog = build_standard_catalog()
    entry = catalog.get("single_contact")
    assert entry is not None
    sheet_id = bus.document.active_sheet_id
    assert sheet_id is not None
    device_id = uuid4()
    fragment_id = uuid4()
    cp1, cp2 = uuid4(), uuid4()
    bus.execute(
        PlaceDeviceCommand(
            device_id=device_id,
            fragment_id=fragment_id,
            sheet_id=sheet_id,
            composition_ref=entry.composition_ref,
            x_mm=50.0,
            y_mm=50.0,
            designation="S1",
            connection_points=((cp1, "1"), (cp2, "2")),
        )
    )
    placed = bus.document.presentations[sheet_id].symbols[0]
    return bus, catalog, placed, cp1, cp2, sheet_id


def test_move_device_updates_position_and_undo() -> None:
    bus, catalog, placed, _, _, sheet_id = _place_single_contact(
        CommandBus(create_empty_project(), ApplicationSettings())
    )
    cmd = build_move_device_command(bus.document, catalog.library, placed, 100.0, 80.0)
    bus.execute(cmd)
    moved = bus.document.presentations[sheet_id].symbols[0]
    assert moved.x_mm == 100.0
    assert moved.y_mm == 80.0
    bus.undo()
    restored = bus.document.presentations[sheet_id].symbols[0]
    assert restored.x_mm == 50.0
    assert restored.y_mm == 50.0


def test_delete_device_removes_symbol() -> None:
    bus, _, _, _, _, sheet_id = _place_single_contact(
        CommandBus(create_empty_project(), ApplicationSettings())
    )
    placed = bus.document.presentations[sheet_id].symbols[0]
    bus.execute(
        DeleteDeviceCommand(
            device_id=placed.device_id,
            fragment_id=placed.fragment_id,
            sheet_id=sheet_id,
        )
    )
    assert bus.document.presentations[sheet_id].symbols == ()
    bus.undo()
    assert len(bus.document.presentations[sheet_id].symbols) == 1


def test_delete_wire_removes_two_pin_net() -> None:
    bus, _, _, cp1, cp2, sheet_id = _place_single_contact(
        CommandBus(create_empty_project(), ApplicationSettings())
    )
    segments = route_orthogonal((50.0, 0.0), (50.0, 20.0))
    connect = build_connect_pins_command(
        bus.document, sheet_id, cp1, cp2, segments, WireKind.CONTROL
    )
    bus.execute(connect)
    assert len(bus.document.nets) == 1
    wire = bus.document.presentations[sheet_id].wires[0]
    bus.execute(DeleteWireCommand(wire_id=wire.wire_id, sheet_id=sheet_id))
    assert bus.document.presentations[sheet_id].wires == ()
    assert len(bus.document.nets) == 0


def test_set_wire_kind() -> None:
    bus, _, _, cp1, cp2, sheet_id = _place_single_contact(
        CommandBus(create_empty_project(), ApplicationSettings())
    )
    segments = (WireSegment(x1_mm=0, y1_mm=0, x2_mm=10, y2_mm=0),)
    connect = build_connect_pins_command(
        bus.document, sheet_id, cp1, cp2, segments, WireKind.CONTROL
    )
    bus.execute(connect)
    wire = bus.document.presentations[sheet_id].wires[0]
    bus.execute(
        SetWireKindCommand(
            wire_id=wire.wire_id,
            sheet_id=sheet_id,
            new_kind=WireKind.PE,
            old_kind=WireKind.CONTROL,
        )
    )
    assert bus.document.presentations[sheet_id].wires[0].wire_kind == WireKind.PE
