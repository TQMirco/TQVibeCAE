"""Test GraphicCompositionResolver."""

from __future__ import annotations

from tqvibecae.resources.iec_graphics import POLE_SPACING_MM, build_demo_library
from tqvibecae.services.rendering.graphic_resolver import GraphicCompositionResolver


def test_three_pole_resolves_six_pins() -> None:
    library, refs = build_demo_library()
    resolver = GraphicCompositionResolver(library)
    resolved = resolver.resolve(refs.three_pole)

    assert len(resolved.pin_anchors) == 6
    assert len(resolved.primitives) == 15  # 5 linee IEC x 3 poli


def test_three_pole_bbox_spans_repeated_spacing() -> None:
    library, refs = build_demo_library()
    resolver = GraphicCompositionResolver(library)
    resolved = resolver.resolve(refs.three_pole)

    width = resolved.bbox_max_x_mm - resolved.bbox_min_x_mm
    assert width >= 2 * POLE_SPACING_MM


def test_sheet_transform_offsets_origin() -> None:
    library, refs = build_demo_library()
    resolver = GraphicCompositionResolver(library)
    at_origin = resolver.resolve(refs.single_contact)
    offset = resolver.resolve(refs.single_contact, origin_x_mm=50.0, origin_y_mm=30.0)

    assert offset.pin_anchors[0].x_mm > at_origin.pin_anchors[0].x_mm
    assert offset.pin_anchors[0].y_mm > at_origin.pin_anchors[0].y_mm


def test_single_contact_has_two_pins_with_symbol_ids() -> None:
    library, refs = build_demo_library()
    resolver = GraphicCompositionResolver(library)
    resolved = resolver.resolve(refs.single_contact)

    assert len(resolved.pin_anchors) == 2
    pin_ids = {pin.symbol_pin_id for pin in resolved.pin_anchors}
    assert pin_ids == {"1", "2"}
