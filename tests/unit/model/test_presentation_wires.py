"""Test presentation wire models."""

from __future__ import annotations

from uuid import uuid4

import pytest
from pydantic import ValidationError

from tqvibecae.model.presentation import (
    SheetPresentation,
    WireGraphic,
    WireKind,
    WireSegment,
    pin_ref,
)


def test_wire_segment_roundtrip() -> None:
    seg = WireSegment(x1_mm=0.0, y1_mm=0.0, x2_mm=10.0, y2_mm=0.0)
    restored = WireSegment.model_validate(seg.model_dump(mode="json"))
    assert restored == seg


def test_wire_graphic_roundtrip() -> None:
    wire = WireGraphic(
        wire_id=uuid4(),
        segments=(WireSegment(x1_mm=0, y1_mm=0, x2_mm=5, y2_mm=0),),
        wire_kind=WireKind.CONTROL,
        from_pin_ref=pin_ref(uuid4()),
        to_pin_ref=pin_ref(uuid4()),
    )
    restored = WireGraphic.model_validate(wire.model_dump(mode="json"))
    assert restored == wire


def test_sheet_presentation_grid_positive() -> None:
    with pytest.raises(ValidationError):
        SheetPresentation(sheet_id=uuid4(), grid_mm=0)
