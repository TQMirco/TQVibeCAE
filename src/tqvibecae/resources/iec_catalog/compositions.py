"""Composizioni simboli IEC da celle base."""

from __future__ import annotations

from tqvibecae.model.catalog_refs import CatalogReference
from tqvibecae.model.entity_types import SYMBOL_GRAPHIC_COMPOSITION
from tqvibecae.model.graphics.cells import GraphicCellDefinition, GraphicCellInstance
from tqvibecae.model.graphics.composition import PinMapping, SymbolGraphicComposition
from tqvibecae.model.graphics.primitives import GraphicTransform
from tqvibecae.resources.iec_catalog.cells import CATALOG_VERSION, cell_ref
from tqvibecae.resources.iec_catalog.uuids import iec_uuid

POLE_SPACING = 14.0


def comp_ref(comp_id: str) -> CatalogReference:
    return CatalogReference(
        definition_id=iec_uuid("composition", comp_id),
        definition_version=CATALOG_VERSION,
        catalog_kind="graphic_composition",
    )


def _single(
    comp_id: str,
    cell_name: str,
    instance_id: str,
    pins: tuple[tuple[str, str, str], ...],
) -> SymbolGraphicComposition:
    return SymbolGraphicComposition(
        id=iec_uuid("composition", comp_id),
        entity_type=SYMBOL_GRAPHIC_COMPOSITION,
        name=comp_id,
        cells=(
            GraphicCellInstance(
                cell_ref=cell_ref(cell_name),
                instance_id=instance_id,
            ),
        ),
        pin_map=tuple(
            PinMapping(
                symbol_pin_id=pin,
                cell_instance_id=inst,
                cell_anchor_id=anchor,
            )
            for pin, inst, anchor in pins
        ),
    )


def _poles(
    comp_id: str,
    cell_name: str,
    count: int,
    pin_names: tuple[str, ...],
) -> SymbolGraphicComposition:
    top_pins = pin_names[:count]
    bottom_pins = pin_names[count:]
    pin_map = []
    for pin in top_pins:
        pin_map.append(
            PinMapping(
                symbol_pin_id=pin, cell_instance_id="poles", cell_anchor_id="top"
            )
        )
    for pin in bottom_pins:
        pin_map.append(
            PinMapping(
                symbol_pin_id=pin, cell_instance_id="poles", cell_anchor_id="bottom"
            )
        )
    return SymbolGraphicComposition(
        id=iec_uuid("composition", comp_id),
        entity_type=SYMBOL_GRAPHIC_COMPOSITION,
        name=comp_id,
        cells=(
            GraphicCellInstance(
                cell_ref=cell_ref(cell_name),
                instance_id="poles",
                repeat_count=count,
                repeat_spacing_mm=POLE_SPACING,
            ),
        ),
        pin_map=tuple(pin_map),
    )


def build_all_compositions(
    cells: dict[str, GraphicCellDefinition],
) -> dict[str, SymbolGraphicComposition]:
    """Costruisce composizioni catalogo — cells param ignorato, per estensione."""
    _ = cells
    compositions: dict[str, SymbolGraphicComposition] = {}

    compositions["single_contact"] = _single(
        "single_contact",
        "contact_no",
        "c1",
        (("1", "c1", "top"), ("2", "c1", "bottom")),
    )
    compositions["single_contact_nc"] = _single(
        "single_contact_nc",
        "contact_nc",
        "c1",
        (("1", "c1", "top"), ("2", "c1", "bottom")),
    )
    compositions["coil"] = _single(
        "coil", "coil", "coil1", (("A1", "coil1", "a1"), ("A2", "coil1", "a2"))
    )
    compositions["fuse"] = _single(
        "fuse", "fuse", "f1", (("1", "f1", "top"), ("2", "f1", "bottom"))
    )
    compositions["mcb_1p"] = _single(
        "mcb_1p",
        "breaker_blade",
        "b1",
        (("1", "b1", "top"), ("2", "b1", "bottom")),
    )
    compositions["mcb_3p"] = _poles(
        "mcb_3p", "breaker_blade", 3, ("L1", "L2", "L3", "T1", "T2", "T3")
    )
    compositions["contactor_3p"] = _poles(
        "contactor_3p", "contact_no", 3, ("L1", "L2", "L3", "T1", "T2", "T3")
    )
    compositions["motor"] = _single(
        "motor",
        "motor_circle",
        "m1",
        (
            ("U", "m1", "u"),
            ("V", "m1", "v"),
            ("W", "m1", "w"),
            ("PE", "m1", "pe"),
        ),
    )
    compositions["lamp"] = _single(
        "lamp", "lamp", "l1", (("1", "l1", "a1"), ("2", "l1", "a2"))
    )
    compositions["terminal"] = _single(
        "terminal", "terminal", "t1", (("1", "t1", "conn"),)
    )
    compositions["junction"] = _single(
        "junction", "junction", "j1", (("1", "j1", "j"),)
    )
    compositions["pe"] = _single("pe", "pe_symbol", "pe1", (("PE", "pe1", "pe"),))
    compositions["pushbutton_no"] = SymbolGraphicComposition(
        id=iec_uuid("composition", "pushbutton_no"),
        entity_type=SYMBOL_GRAPHIC_COMPOSITION,
        name="pushbutton_no",
        cells=(
            GraphicCellInstance(
                cell_ref=cell_ref("pushbutton_head"), instance_id="head"
            ),
            GraphicCellInstance(
                cell_ref=cell_ref("contact_no"),
                instance_id="contact",
                transform=GraphicTransform(translate_y_mm=10.0),
            ),
        ),
        pin_map=(
            PinMapping(
                symbol_pin_id="1", cell_instance_id="contact", cell_anchor_id="top"
            ),
            PinMapping(
                symbol_pin_id="2", cell_instance_id="contact", cell_anchor_id="bottom"
            ),
        ),
    )
    compositions["pushbutton_nc"] = SymbolGraphicComposition(
        id=iec_uuid("composition", "pushbutton_nc"),
        entity_type=SYMBOL_GRAPHIC_COMPOSITION,
        name="pushbutton_nc",
        cells=(
            GraphicCellInstance(
                cell_ref=cell_ref("pushbutton_head"), instance_id="head"
            ),
            GraphicCellInstance(
                cell_ref=cell_ref("contact_nc"),
                instance_id="contact",
                transform=GraphicTransform(translate_y_mm=10.0),
            ),
        ),
        pin_map=(
            PinMapping(
                symbol_pin_id="1", cell_instance_id="contact", cell_anchor_id="top"
            ),
            PinMapping(
                symbol_pin_id="2", cell_instance_id="contact", cell_anchor_id="bottom"
            ),
        ),
    )
    compositions["transformer"] = _single(
        "transformer",
        "transformer_core",
        "tr1",
        (
            ("P1", "tr1", "p1"),
            ("P2", "tr1", "p2"),
            ("S1", "tr1", "s1"),
            ("S2", "tr1", "s2"),
        ),
    )
    compositions["ammeter"] = _single(
        "ammeter", "ammeter", "a1", (("1", "a1", "in"), ("2", "a1", "out"))
    )
    compositions["three_pole_contacts"] = _poles(
        "three_pole_contacts", "contact_no", 3, ("L1", "L2", "L3", "T1", "T2", "T3")
    )
    return compositions
