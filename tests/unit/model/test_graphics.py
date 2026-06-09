"""Test modelli grafici — round-trip e validator."""

from __future__ import annotations

from uuid import uuid4

import pytest
from pydantic import ValidationError

from tqvibecae.model.catalog_refs import CatalogReference
from tqvibecae.model.entity_types import GRAPHIC_CELL
from tqvibecae.model.graphics.cells import GraphicCellDefinition, GraphicCellInstance
from tqvibecae.model.graphics.composition import SymbolGraphicComposition
from tqvibecae.model.graphics.primitives import GraphicPrimitive, PinAnchor
from tqvibecae.resources.iec_graphics import (
    build_demo_library,
    build_three_pole_composition,
)


def test_graphic_cell_json_roundtrip() -> None:
    cell = GraphicCellDefinition(
        id=uuid4(),
        entity_type=GRAPHIC_CELL,
        name="test",
        category="contact_no",
        width_mm=10.0,
        height_mm=20.0,
        primitives=(
            GraphicPrimitive(
                primitive_type="line",
                geometry={"x1": 0.0, "y1": 0.0, "x2": 1.0, "y2": 1.0},
            ),
        ),
        pin_anchors=(PinAnchor(anchor_id="p1", x=0.5, y=0.0),),
    )
    data = cell.model_dump(mode="json")
    restored = GraphicCellDefinition.model_validate(data)
    assert restored == cell


def test_graphic_cell_instance_requires_spacing_for_repeat() -> None:
    ref = CatalogReference(
        definition_id=uuid4(),
        definition_version=1,
        catalog_kind="graphic_cell",
    )
    with pytest.raises(ValidationError):
        GraphicCellInstance(
            cell_ref=ref,
            instance_id="x",
            repeat_count=3,
        )


def test_three_pole_composition_validates() -> None:
    comp = build_three_pole_composition()
    data = comp.model_dump(mode="json")
    restored = SymbolGraphicComposition.model_validate(data)
    assert restored.name == "three_pole_contacts"
    assert restored.cells[0].repeat_count == 3


def test_demo_library_registers_all_entries() -> None:
    library, refs = build_demo_library()
    library.get_composition(refs.three_pole)
    library.get_composition(refs.single_contact)
    library.get_composition(refs.coil)
