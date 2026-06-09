"""Celle grafiche base IEC 60617 / CEI 3-7.

Geometria allineata a docs/idea/guida-progettazione-schema-elettrico.md:
flusso verticale contatti (stato a riposo), simboli funzione IEC 81346-2.
"""

from __future__ import annotations

from tqvibecae.model.catalog_refs import CatalogReference
from tqvibecae.model.entity_types import GRAPHIC_CELL
from tqvibecae.model.graphics.cells import GraphicCellDefinition
from tqvibecae.model.graphics.primitives import GraphicPrimitive, PinAnchor
from tqvibecae.resources.iec_catalog.uuids import iec_uuid

CATALOG_VERSION = 1
CELL_W = 12.0
CELL_H = 20.0


def cell_ref(cell_id: str) -> CatalogReference:
    uid = iec_uuid("cell", cell_id)
    return CatalogReference(
        definition_id=uid,
        definition_version=CATALOG_VERSION,
        catalog_kind="graphic_cell",
    )


def _line(x1: float, y1: float, x2: float, y2: float) -> GraphicPrimitive:
    return GraphicPrimitive(
        primitive_type="line",
        geometry={"x1": x1, "y1": y1, "x2": x2, "y2": y2},
    )


def _rect(x: float, y: float, width: float, height: float) -> GraphicPrimitive:
    return GraphicPrimitive(
        primitive_type="rect",
        geometry={"x": x, "y": y, "width": width, "height": height},
    )


def _circle(cx: float, cy: float, radius: float) -> GraphicPrimitive:
    return GraphicPrimitive(
        primitive_type="circle",
        geometry={"cx": cx, "cy": cy, "radius": radius},
    )


def _letter(x: float, y: float, char: str, scale: float = 0.12) -> GraphicPrimitive:
    return GraphicPrimitive(
        primitive_type="text",
        geometry={
            "x": x,
            "y": y,
            "text_scale": scale,
            "text_char": ord(char),
        },
    )


def build_all_cells() -> dict[str, GraphicCellDefinition]:
    """Costruisce tutte le celle base del catalogo."""
    cells: dict[str, GraphicCellDefinition] = {}

    # IEC 60617 S00220 — contatto NA (stato a riposo: aperto)
    cells["contact_no"] = GraphicCellDefinition(
        id=iec_uuid("cell", "contact_no"),
        entity_type=GRAPHIC_CELL,
        name="contact_no",
        category="contact_no",
        width_mm=CELL_W,
        height_mm=CELL_H,
        primitives=(
            _line(0.5, 0.0, 0.5, 0.38),
            _line(0.30, 0.38, 0.70, 0.38),
            _line(0.30, 0.38, 0.70, 0.58),
            _line(0.30, 0.62, 0.70, 0.62),
            _line(0.5, 0.62, 0.5, 1.0),
        ),
        pin_anchors=(
            PinAnchor(anchor_id="top", x=0.5, y=0.0),
            PinAnchor(anchor_id="bottom", x=0.5, y=1.0),
        ),
    )

    # IEC 60617 S00221 — contatto NC (stato a riposo: chiuso)
    cells["contact_nc"] = GraphicCellDefinition(
        id=iec_uuid("cell", "contact_nc"),
        entity_type=GRAPHIC_CELL,
        name="contact_nc",
        category="contact_nc",
        width_mm=CELL_W,
        height_mm=CELL_H,
        primitives=(
            _line(0.5, 0.0, 0.5, 0.38),
            _line(0.30, 0.38, 0.70, 0.38),
            _line(0.30, 0.38, 0.70, 0.62),
            _line(0.30, 0.62, 0.70, 0.62),
            _line(0.5, 0.62, 0.5, 1.0),
        ),
        pin_anchors=(
            PinAnchor(anchor_id="top", x=0.5, y=0.0),
            PinAnchor(anchor_id="bottom", x=0.5, y=1.0),
        ),
    )

    # IEC 60617 S00262 — bobina relè / contattore
    cells["coil"] = GraphicCellDefinition(
        id=iec_uuid("cell", "coil"),
        entity_type=GRAPHIC_CELL,
        name="coil",
        category="coil",
        width_mm=18.0,
        height_mm=16.0,
        primitives=(
            _line(0.0, 0.5, 0.12, 0.5),
            _rect(0.12, 0.22, 0.76, 0.56),
            _line(0.88, 0.5, 1.0, 0.5),
        ),
        pin_anchors=(
            PinAnchor(anchor_id="a1", x=0.0, y=0.5),
            PinAnchor(anchor_id="a2", x=1.0, y=0.5),
        ),
    )

    # IEC 60617 S00279 — fusibile
    cells["fuse"] = GraphicCellDefinition(
        id=iec_uuid("cell", "fuse"),
        entity_type=GRAPHIC_CELL,
        name="fuse",
        category="fuse",
        width_mm=10.0,
        height_mm=24.0,
        primitives=(
            _line(0.5, 0.0, 0.5, 0.20),
            _rect(0.22, 0.20, 0.56, 0.60),
            _line(0.30, 0.50, 0.70, 0.50),
            _line(0.5, 0.80, 0.5, 1.0),
        ),
        pin_anchors=(
            PinAnchor(anchor_id="top", x=0.5, y=0.0),
            PinAnchor(anchor_id="bottom", x=0.5, y=1.0),
        ),
    )

    # IEC 60617 S00325 — interruttore automatico (magnetotermico)
    cells["breaker_blade"] = GraphicCellDefinition(
        id=iec_uuid("cell", "breaker_blade"),
        entity_type=GRAPHIC_CELL,
        name="breaker_blade",
        category="breaker",
        width_mm=14.0,
        height_mm=24.0,
        primitives=(
            _line(0.5, 0.0, 0.5, 0.16),
            _rect(0.26, 0.16, 0.48, 0.58),
            _line(0.36, 0.28, 0.64, 0.28),
            _line(0.36, 0.28, 0.62, 0.48),
            _line(0.36, 0.52, 0.64, 0.52),
            _line(0.72, 0.40, 0.88, 0.56),
            _line(0.5, 0.74, 0.5, 1.0),
        ),
        pin_anchors=(
            PinAnchor(anchor_id="top", x=0.5, y=0.0),
            PinAnchor(anchor_id="bottom", x=0.5, y=1.0),
        ),
    )

    # IEC 60617 S00046 — motore trifase
    cells["motor_circle"] = GraphicCellDefinition(
        id=iec_uuid("cell", "motor_circle"),
        entity_type=GRAPHIC_CELL,
        name="motor_circle",
        category="motor",
        width_mm=22.0,
        height_mm=24.0,
        primitives=(
            _circle(0.58, 0.50, 0.34),
            _letter(0.50, 0.58, "M", 0.14),
            _line(0.0, 0.35, 0.24, 0.35),
            _line(0.0, 0.50, 0.24, 0.50),
            _line(0.0, 0.65, 0.24, 0.65),
            _line(0.58, 0.84, 0.58, 1.0),
        ),
        pin_anchors=(
            PinAnchor(anchor_id="u", x=0.0, y=0.35),
            PinAnchor(anchor_id="v", x=0.0, y=0.50),
            PinAnchor(anchor_id="w", x=0.0, y=0.65),
            PinAnchor(anchor_id="pe", x=0.58, y=1.0),
        ),
    )

    # IEC 60617 S00774 — lampada / segnalazione (-H)
    cells["lamp"] = GraphicCellDefinition(
        id=iec_uuid("cell", "lamp"),
        entity_type=GRAPHIC_CELL,
        name="lamp",
        category="lamp",
        width_mm=18.0,
        height_mm=16.0,
        primitives=(
            _line(0.0, 0.5, 0.18, 0.5),
            _circle(0.50, 0.50, 0.32),
            _line(0.22, 0.22, 0.78, 0.78),
            _line(0.78, 0.22, 0.22, 0.78),
            _line(0.82, 0.5, 1.0, 0.5),
        ),
        pin_anchors=(
            PinAnchor(anchor_id="a1", x=0.0, y=0.5),
            PinAnchor(anchor_id="a2", x=1.0, y=0.5),
        ),
    )

    # IEC 60617 S00038 — punto di connessione / morsetto (-X)
    cells["terminal"] = GraphicCellDefinition(
        id=iec_uuid("cell", "terminal"),
        entity_type=GRAPHIC_CELL,
        name="terminal",
        category="terminal",
        width_mm=10.0,
        height_mm=8.0,
        primitives=(
            _line(0.0, 0.5, 0.38, 0.5),
            _circle(0.58, 0.50, 0.18),
        ),
        pin_anchors=(PinAnchor(anchor_id="conn", x=0.58, y=0.5),),
    )

    # IEC 60617 S00125 — giunto fili
    cells["junction"] = GraphicCellDefinition(
        id=iec_uuid("cell", "junction"),
        entity_type=GRAPHIC_CELL,
        name="junction",
        category="junction",
        width_mm=4.0,
        height_mm=4.0,
        primitives=(_circle(0.5, 0.5, 0.40),),
        pin_anchors=(PinAnchor(anchor_id="j", x=0.5, y=0.5),),
    )

    # IEC 60417 / 60617 — simbolo terra protezione PE
    cells["pe_symbol"] = GraphicCellDefinition(
        id=iec_uuid("cell", "pe_symbol"),
        entity_type=GRAPHIC_CELL,
        name="pe_symbol",
        category="pe",
        width_mm=14.0,
        height_mm=16.0,
        primitives=(
            _line(0.5, 0.0, 0.5, 0.42),
            _line(0.12, 0.52, 0.88, 0.52),
            _line(0.22, 0.66, 0.78, 0.66),
            _line(0.32, 0.80, 0.68, 0.80),
        ),
        pin_anchors=(PinAnchor(anchor_id="pe", x=0.5, y=0.0),),
    )

    # IEC 60617 S00263 — testa operatore pulsante (sopra contatto)
    cells["pushbutton_head"] = GraphicCellDefinition(
        id=iec_uuid("cell", "pushbutton_head"),
        entity_type=GRAPHIC_CELL,
        name="pushbutton_head",
        category="pushbutton",
        width_mm=14.0,
        height_mm=12.0,
        primitives=(
            _circle(0.5, 0.30, 0.22),
            _line(0.5, 0.52, 0.5, 1.0),
        ),
        pin_anchors=(PinAnchor(anchor_id="bottom", x=0.5, y=1.0),),
    )

    # IEC 60617 S01055 — trasformatore (-T), avvolgimenti come semicerchi accoppiati
    cells["transformer_core"] = GraphicCellDefinition(
        id=iec_uuid("cell", "transformer_core"),
        entity_type=GRAPHIC_CELL,
        name="transformer_core",
        category="transformer",
        width_mm=22.0,
        height_mm=28.0,
        primitives=(
            _circle(0.34, 0.50, 0.22),
            _circle(0.66, 0.50, 0.22),
            _line(0.34, 0.0, 0.34, 0.28),
            _line(0.34, 0.72, 0.34, 1.0),
            _line(0.66, 0.0, 0.66, 0.28),
            _line(0.66, 0.72, 0.66, 1.0),
        ),
        pin_anchors=(
            PinAnchor(anchor_id="p1", x=0.34, y=0.0),
            PinAnchor(anchor_id="p2", x=0.34, y=1.0),
            PinAnchor(anchor_id="s1", x=0.66, y=0.0),
            PinAnchor(anchor_id="s2", x=0.66, y=1.0),
        ),
    )

    # IEC 60617 S00761 — amperometro
    cells["ammeter"] = GraphicCellDefinition(
        id=iec_uuid("cell", "ammeter"),
        entity_type=GRAPHIC_CELL,
        name="ammeter",
        category="ammeter",
        width_mm=18.0,
        height_mm=18.0,
        primitives=(
            _line(0.0, 0.5, 0.16, 0.5),
            _circle(0.50, 0.50, 0.34),
            _letter(0.40, 0.60, "A", 0.12),
            _line(0.84, 0.5, 1.0, 0.5),
        ),
        pin_anchors=(
            PinAnchor(anchor_id="in", x=0.0, y=0.5),
            PinAnchor(anchor_id="out", x=1.0, y=0.5),
        ),
    )
    return cells
