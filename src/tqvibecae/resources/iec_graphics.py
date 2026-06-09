"""Backward compatibility — re-export demo library from catalogo IEC."""

from __future__ import annotations

from dataclasses import dataclass

from tqvibecae.model.catalog_refs import CatalogReference
from tqvibecae.resources.iec_catalog.catalog import build_standard_catalog
from tqvibecae.services.rendering.graphic_resolver import InMemoryGraphicLibrary

CONTACT_NO_ID = None  # deprecated — use catalog UUIDs
CATALOG_VERSION = 1
CELL_WIDTH_MM = 12.0
CELL_HEIGHT_MM = 20.0
POLE_SPACING_MM = 14.0


@dataclass(frozen=True, slots=True)
class DemoGraphicRefs:
    """Riferimenti catalogo per composizioni demo legacy."""

    single_contact: CatalogReference
    three_pole: CatalogReference
    coil: CatalogReference


def build_demo_library() -> tuple[InMemoryGraphicLibrary, DemoGraphicRefs]:
    """Compatibilita test esistenti — usa catalogo standard."""
    catalog = build_standard_catalog()
    single = catalog.get("single_contact")
    three = catalog.get("three_pole_contacts")
    coil = catalog.get("coil")
    assert single and three and coil
    refs = DemoGraphicRefs(
        single_contact=single.composition_ref,
        three_pole=three.composition_ref,
        coil=coil.composition_ref,
    )
    return catalog.library, refs


def build_contact_no_cell():
    from tqvibecae.resources.iec_catalog.cells import build_all_cells

    return build_all_cells()["contact_no"]


def build_three_pole_composition():
    from tqvibecae.resources.iec_catalog.compositions import build_all_compositions

    return build_all_compositions({})["three_pole_contacts"]
