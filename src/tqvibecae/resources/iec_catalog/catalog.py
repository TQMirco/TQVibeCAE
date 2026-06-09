"""Catalogo simboli IEC per palette CAD."""

from __future__ import annotations

from dataclasses import dataclass

from tqvibecae.model.catalog_refs import CatalogReference
from tqvibecae.resources.iec_catalog.cells import build_all_cells
from tqvibecae.resources.iec_catalog.compositions import (
    build_all_compositions,
    comp_ref,
)
from tqvibecae.services.rendering.graphic_resolver import InMemoryGraphicLibrary

CATALOG_ENTRIES: tuple[tuple[str, str, str, str], ...] = (
    ("fuse", "protection", "Fusibile", "fuse"),
    ("mcb_1p", "protection", "Interruttore 1P", "mcb_1p"),
    ("mcb_3p", "protection", "Interruttore 3P", "mcb_3p"),
    ("contactor_3p", "switching", "Contattore 3P", "contactor_3p"),
    ("single_contact", "control", "Contatto NA", "single_contact"),
    ("single_contact_nc", "control", "Contatto NC", "single_contact_nc"),
    ("coil", "control", "Bobina", "coil"),
    ("pushbutton_no", "control", "Pulsante NA", "pushbutton_no"),
    ("pushbutton_nc", "control", "Pulsante NC", "pushbutton_nc"),
    ("motor", "loads", "Motore", "motor"),
    ("lamp", "loads", "Lampada", "lamp"),
    ("terminal", "terminals", "Morsetto", "terminal"),
    ("junction", "terminals", "Giunto", "junction"),
    ("pe", "reference", "Terra PE", "pe"),
    ("ammeter", "measurement", "Amperometro", "ammeter"),
    ("transformer", "transformers", "Trasformatore", "transformer"),
    ("three_pole_contacts", "switching", "3 contatti", "three_pole_contacts"),
)


@dataclass(frozen=True, slots=True)
class IecSymbolCatalogEntry:
    """Voce palette simbolo IEC."""

    catalog_id: str
    category: str
    label: str
    composition_ref: CatalogReference


@dataclass(frozen=True, slots=True)
class IecSymbolCatalog:
    """Catalogo in-memory con lookup per categoria."""

    library: InMemoryGraphicLibrary
    entries: tuple[IecSymbolCatalogEntry, ...]

    def by_category(self) -> dict[str, tuple[IecSymbolCatalogEntry, ...]]:
        grouped: dict[str, list[IecSymbolCatalogEntry]] = {}
        for entry in self.entries:
            grouped.setdefault(entry.category, []).append(entry)
        return {k: tuple(v) for k, v in sorted(grouped.items())}

    def get(self, catalog_id: str) -> IecSymbolCatalogEntry | None:
        for entry in self.entries:
            if entry.catalog_id == catalog_id:
                return entry
        return None


def build_standard_catalog() -> IecSymbolCatalog:
    """Costruisce libreria IEC completa per editor CAD."""
    cells = build_all_cells()
    compositions = build_all_compositions(cells)
    library = InMemoryGraphicLibrary()
    for cell in cells.values():
        library.register_cell(cell)
    for composition in compositions.values():
        library.register_composition(composition)

    entries: list[IecSymbolCatalogEntry] = []
    for catalog_id, category, label, comp_key in CATALOG_ENTRIES:
        entries.append(
            IecSymbolCatalogEntry(
                catalog_id=catalog_id,
                category=category,
                label=label,
                composition_ref=comp_ref(comp_key),
            )
        )
    return IecSymbolCatalog(library=library, entries=tuple(entries))
