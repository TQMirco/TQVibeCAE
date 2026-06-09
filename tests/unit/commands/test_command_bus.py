"""Test CommandBus undo/redo."""

from __future__ import annotations

from uuid import uuid4

from tqvibecae.commands.command_bus import CommandBus
from tqvibecae.commands.connect_helpers import build_connect_pins_command
from tqvibecae.commands.place_device import PlaceDeviceCommand
from tqvibecae.commands.project_factory import create_empty_project, project_to_manifest
from tqvibecae.resources.iec_catalog.catalog import build_standard_catalog
from tqvibecae.services.rendering.wire_router import route_orthogonal


def test_place_device_undo_redo() -> None:
    catalog = build_standard_catalog()
    entry = catalog.get("single_contact")
    assert entry is not None
    doc = create_empty_project()
    sheet_id = doc.active_sheet_id
    assert sheet_id is not None
    bus = CommandBus(doc)
    device_id = uuid4()
    fragment_id = uuid4()
    cp1, cp2 = uuid4(), uuid4()
    cmd = PlaceDeviceCommand(
        device_id=device_id,
        fragment_id=fragment_id,
        sheet_id=sheet_id,
        composition_ref=entry.composition_ref,
        x_mm=20.0,
        y_mm=30.0,
        designation="Q1",
        connection_points=((cp1, "1"), (cp2, "2")),
    )
    bus.execute(cmd)
    assert device_id in doc.devices
    assert bus.undo()
    assert device_id not in doc.devices
    assert bus.redo()
    assert device_id in doc.devices


def test_connect_pins_creates_net() -> None:
    catalog = build_standard_catalog()
    entry = catalog.get("single_contact")
    assert entry is not None
    doc = create_empty_project()
    sheet_id = doc.active_sheet_id
    assert sheet_id is not None
    bus = CommandBus(doc)
    cp1, cp2 = uuid4(), uuid4()
    bus.execute(
        PlaceDeviceCommand(
            device_id=uuid4(),
            fragment_id=uuid4(),
            sheet_id=sheet_id,
            composition_ref=entry.composition_ref,
            x_mm=10.0,
            y_mm=10.0,
            designation="Q1",
            connection_points=((cp1, "1"), (cp2, "2")),
        )
    )
    segments = route_orthogonal((10.0, 0.0), (10.0, 20.0))
    connect = build_connect_pins_command(doc, sheet_id, cp1, cp2, segments)
    bus.execute(connect)
    assert len(doc.nets) == 1
    presentation = doc.presentations[sheet_id]
    assert len(presentation.wires) == 1


def test_project_to_manifest() -> None:
    doc = create_empty_project()
    manifest = project_to_manifest(doc)
    assert manifest.project_id == doc.project.id
