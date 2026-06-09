"""Test catalogo IEC standard."""

from __future__ import annotations

from tqvibecae.resources.iec_catalog.catalog import build_standard_catalog
from tqvibecae.services.rendering.graphic_resolver import GraphicCompositionResolver


def test_standard_catalog_resolves_all() -> None:
    catalog = build_standard_catalog()
    resolver = GraphicCompositionResolver(catalog.library)
    assert len(catalog.entries) >= 15
    for entry in catalog.entries:
        resolved = resolver.resolve(entry.composition_ref)
        assert len(resolved.pin_anchors) >= 1
