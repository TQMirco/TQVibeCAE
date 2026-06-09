"""Controller scene CAD — item grafici persistenti e stile IEC."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QBrush, QColor, QFont, QPainterPath, QPen
from PySide6.QtWidgets import (
    QGraphicsEllipseItem,
    QGraphicsItem,
    QGraphicsItemGroup,
    QGraphicsLineItem,
    QGraphicsPathItem,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsSimpleTextItem,
)

from tqvibecae.model.presentation import WireGraphic, WireKind
from tqvibecae.services.rendering.graphic_resolver import (
    ResolvedPinAnchor,
    ResolvedPrimitive,
)
from tqvibecae.viewmodel.schematic_editor_vm import (
    EditorOverlayView,
    EditorSheetView,
    PinHit,
    ToolMode,
)

SHEET_WIDTH_MM = 420.0
SHEET_HEIGHT_MM = 297.0
MAJOR_GRID_MM = 5.0
MINOR_GRID_MM = 2.5

SYMBOL_PEN = QPen(QColor(20, 20, 30))
SYMBOL_PEN.setWidthF(0.8)
SYMBOL_PEN.setCapStyle(Qt.PenCapStyle.SquareCap)

WIRE_COLORS = {
    WireKind.POWER: QColor(60, 40, 20),
    WireKind.CONTROL: QColor(50, 50, 60),
    WireKind.PE: QColor(80, 160, 48),
}

WIRE_WIDTHS = {
    WireKind.POWER: 1.5,
    WireKind.CONTROL: 0.8,
    WireKind.PE: 1.2,
}


def wire_pen(kind: WireKind) -> QPen:
    pen = QPen(WIRE_COLORS.get(kind, WIRE_COLORS[WireKind.CONTROL]))
    pen.setWidthF(WIRE_WIDTHS.get(kind, 0.8))
    pen.setCapStyle(Qt.PenCapStyle.SquareCap)
    return pen


def _arc_path(
    cx: float,
    cy: float,
    radius: float,
    start_deg: float,
    span_deg: float,
) -> QPainterPath:
    path = QPainterPath()
    rect_x = cx - radius
    rect_y = cy - radius
    path.arcMoveTo(rect_x, rect_y, radius * 2, radius * 2, start_deg)
    path.arcTo(rect_x, rect_y, radius * 2, radius * 2, start_deg, span_deg)
    return path


class PinGraphicsItem(QGraphicsEllipseItem):
    """Pin cliccabile — visibile in modalità filo o hover."""

    def __init__(
        self,
        connection_point_id: UUID,
        x_mm: float,
        y_mm: float,
        radius: float = 2.0,
    ) -> None:
        super().__init__(-radius, -radius, radius * 2, radius * 2)
        self.connection_point_id = connection_point_id
        self.setPos(x_mm, y_mm)
        self.setPen(QPen(QColor(40, 120, 60)))
        self.setBrush(QBrush(QColor(120, 220, 140)))
        self.setZValue(20)
        self.setVisible(False)
        self.setAcceptHoverEvents(True)

    def hoverEnterEvent(self, event) -> None:
        self.setBrush(QBrush(QColor(160, 255, 180)))
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event) -> None:
        self.setBrush(QBrush(QColor(120, 220, 140)))
        super().hoverLeaveEvent(event)


class SymbolGraphicsItem(QGraphicsItemGroup):
    """Gruppo simbolo con metadati selezione."""

    def __init__(
        self,
        fragment_id: UUID,
        device_id: UUID,
        label: str,
        graphic_primitives: tuple[ResolvedPrimitive, ...],
        pin_anchors: tuple[ResolvedPinAnchor, ...],
        pin_hits: tuple[PinHit, ...],
        label_x_mm: float = 0.0,
        label_y_mm: float = -10.0,
    ) -> None:
        super().__init__()
        self.fragment_id = fragment_id
        self.device_id = device_id
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setZValue(10)
        self._pin_items: list[PinGraphicsItem] = []

        for primitive in graphic_primitives:
            self._add_primitive(primitive)

        if label:
            text = QGraphicsSimpleTextItem(label)
            font = QFont("Segoe UI", 8)
            text.setFont(font)
            text.setPos(label_x_mm, label_y_mm - 8.0)
            self.addToGroup(text)

        cp_by_pin: dict[str, UUID] = {}
        for hit in pin_hits:
            for pin in pin_anchors:
                if (
                    pin.symbol_pin_id
                    and abs(pin.x_mm - hit.x_mm) < 0.5
                    and abs(pin.y_mm - hit.y_mm) < 0.5
                ):
                    cp_by_pin[pin.symbol_pin_id] = hit.connection_point_id
                    break

        for pin in pin_anchors:
            cp_id = cp_by_pin.get(pin.symbol_pin_id or "")
            if cp_id is None:
                for hit in pin_hits:
                    if (
                        abs(pin.x_mm - hit.x_mm) < 0.5
                        and abs(pin.y_mm - hit.y_mm) < 0.5
                    ):
                        cp_id = hit.connection_point_id
                        break
            if cp_id is not None:
                pin_item = PinGraphicsItem(cp_id, pin.x_mm, pin.y_mm)
                self._pin_items.append(pin_item)
                self.addToGroup(pin_item)

    def _add_primitive(self, primitive: ResolvedPrimitive) -> None:
        geom = primitive.geometry
        if primitive.primitive_type == "line":
            item = QGraphicsLineItem(geom["x1"], geom["y1"], geom["x2"], geom["y2"])
            item.setPen(SYMBOL_PEN)
            self.addToGroup(item)
        elif primitive.primitive_type == "rect":
            item = QGraphicsRectItem(
                geom["x"], geom["y"], geom["width"], geom["height"]
            )
            item.setPen(SYMBOL_PEN)
            item.setBrush(QBrush(Qt.BrushStyle.NoBrush))
            self.addToGroup(item)
        elif primitive.primitive_type == "circle":
            cx, cy, r = geom["cx"], geom["cy"], geom["radius"]
            item = QGraphicsEllipseItem(cx - r, cy - r, r * 2, r * 2)
            item.setPen(SYMBOL_PEN)
            item.setBrush(QBrush(Qt.BrushStyle.NoBrush))
            self.addToGroup(item)
        elif primitive.primitive_type == "arc":
            path = _arc_path(
                geom["cx"],
                geom["cy"],
                geom["radius"],
                geom.get("start_deg", 0.0),
                geom.get("span_deg", 180.0),
            )
            item = QGraphicsPathItem(path)
            item.setPen(SYMBOL_PEN)
            self.addToGroup(item)
        elif primitive.primitive_type == "text":
            char_code = int(geom.get("text_char", ord("M")))
            text = QGraphicsSimpleTextItem(chr(char_code))
            text.setPos(geom["x"], geom["y"])
            self.addToGroup(text)

    def set_pins_visible(self, visible: bool) -> None:
        for pin in self._pin_items:
            pin.setVisible(visible)

    def pin_at_scene_pos(
        self, x_mm: float, y_mm: float, tolerance: float = 4.0
    ) -> UUID | None:
        for pin in self._pin_items:
            pos = pin.scenePos()
            if abs(pos.x() - x_mm) <= tolerance and abs(pos.y() - y_mm) <= tolerance:
                return pin.connection_point_id
        return None


class WireGraphicsItem(QGraphicsItemGroup):
    """Gruppo segmenti filo."""

    def __init__(self, wire_id: UUID, wire: WireGraphic) -> None:
        super().__init__()
        self.wire_id = wire_id
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setZValue(5)
        pen = wire_pen(wire.wire_kind)
        for segment in wire.segments:
            item = QGraphicsLineItem(
                segment.x1_mm,
                segment.y1_mm,
                segment.x2_mm,
                segment.y2_mm,
            )
            item.setPen(pen)
            self.addToGroup(item)


@dataclass(frozen=True, slots=True)
class SceneSyncResult:
    """Metadati dopo sync scene."""

    symbol_items: tuple[SymbolGraphicsItem, ...]
    wire_items: tuple[WireGraphicsItem, ...]


class SchematicSceneController:
    """Sincronizza EditorSheetView con QGraphicsScene preservando la gerarchia."""

    def __init__(self, scene: QGraphicsScene) -> None:
        self._scene = scene
        self._grid_items: list[QGraphicsItem] = []
        self._sheet_rect: QGraphicsRectItem | None = None
        self._symbol_items: list[SymbolGraphicsItem] = []
        self._wire_items: list[WireGraphicsItem] = []
        self._junction_items: list[QGraphicsEllipseItem] = []
        self._overlay_items: list[QGraphicsItem] = []
        self._selection_rect: QGraphicsRectItem | None = None
        self._zoom_preserved = False

    @property
    def zoom_preserved(self) -> bool:
        return self._zoom_preserved

    def mark_zoom_preserved(self) -> None:
        self._zoom_preserved = True

    def sync(
        self,
        view: EditorSheetView,
        overlay: EditorOverlayView | None = None,
        *,
        selected_fragment_id: UUID | None = None,
        selected_wire_id: UUID | None = None,
        tool_mode: ToolMode = ToolMode.SELECT,
    ) -> SceneSyncResult:
        self._clear_dynamic()
        self._draw_sheet_background(view.grid_mm)
        symbol_items: list[SymbolGraphicsItem] = []
        for idx, placement in enumerate(view.placements):
            device_id = (
                view.device_ids[idx] if idx < len(view.device_ids) else UUID(int=0)
            )
            fragment_id = (
                view.fragment_ids[idx] if idx < len(view.fragment_ids) else UUID(int=0)
            )
            pin_hits_for_symbol = tuple(
                h for h in view.pin_hits if h.device_id == device_id
            )
            item = SymbolGraphicsItem(
                fragment_id=fragment_id,
                device_id=device_id,
                label=placement.label,
                graphic_primitives=placement.graphic.primitives,
                pin_anchors=placement.graphic.pin_anchors,
                pin_hits=pin_hits_for_symbol,
                label_x_mm=placement.graphic.bbox_min_x_mm,
                label_y_mm=placement.graphic.bbox_min_y_mm,
            )
            show_pins = tool_mode == ToolMode.WIRE
            item.set_pins_visible(show_pins)
            if selected_fragment_id == item.fragment_id:
                item.setSelected(True)
            self._scene.addItem(item)
            symbol_items.append(item)
            self._symbol_items.append(item)

        wire_items: list[WireGraphicsItem] = []
        for wire in view.wires:
            if isinstance(wire, WireGraphic):
                item = WireGraphicsItem(wire.wire_id, wire)
                if selected_wire_id == wire.wire_id:
                    item.setSelected(True)
                self._scene.addItem(item)
                wire_items.append(item)
                self._wire_items.append(item)

        self._draw_junctions(view)
        if overlay is not None:
            self._draw_overlay(overlay)
        return SceneSyncResult(
            symbol_items=tuple(symbol_items),
            wire_items=tuple(wire_items),
        )

    def _clear_dynamic(self) -> None:
        for item in (
            self._symbol_items
            + self._wire_items
            + self._junction_items
            + self._overlay_items
        ):
            self._scene.removeItem(item)
        self._symbol_items.clear()
        self._wire_items.clear()
        self._junction_items.clear()
        self._overlay_items.clear()
        if self._selection_rect is not None:
            self._scene.removeItem(self._selection_rect)
            self._selection_rect = None

    def _draw_sheet_background(self, grid_mm: float) -> None:
        if self._sheet_rect is not None:
            return
        sheet_pen = QPen(QColor(180, 180, 190))
        sheet_pen.setWidthF(0.5)
        self._sheet_rect = QGraphicsRectItem(0, 0, SHEET_WIDTH_MM, SHEET_HEIGHT_MM)
        self._sheet_rect.setPen(sheet_pen)
        self._sheet_rect.setBrush(QBrush(QColor(255, 255, 255)))
        self._sheet_rect.setZValue(-10)
        self._scene.addItem(self._sheet_rect)

        minor_pen = QPen(QColor(235, 235, 240))
        minor_pen.setWidthF(0.15)
        major_pen = QPen(QColor(220, 220, 228))
        major_pen.setWidthF(0.25)
        step_minor = int(MINOR_GRID_MM)
        step_major = int(max(grid_mm, MAJOR_GRID_MM))
        for x in range(0, int(SHEET_WIDTH_MM) + step_minor, step_minor):
            pen = major_pen if x % step_major == 0 else minor_pen
            line = self._scene.addLine(x, 0, x, SHEET_HEIGHT_MM, pen)
            line.setZValue(-9)
            self._grid_items.append(line)
        for y in range(0, int(SHEET_HEIGHT_MM) + step_minor, step_minor):
            pen = major_pen if y % step_major == 0 else minor_pen
            line = self._scene.addLine(0, y, SHEET_WIDTH_MM, y, pen)
            line.setZValue(-9)
            self._grid_items.append(line)

    def _draw_junctions(self, view: EditorSheetView) -> None:
        endpoint_counts: dict[tuple[float, float], int] = {}
        for wire in view.wires:
            if not isinstance(wire, WireGraphic):
                continue
            for segment in wire.segments:
                for point in (
                    (segment.x1_mm, segment.y1_mm),
                    (segment.x2_mm, segment.y2_mm),
                ):
                    key = (round(point[0], 2), round(point[1], 2))
                    endpoint_counts[key] = endpoint_counts.get(key, 0) + 1
        junction_pen = QPen(QColor(20, 20, 30))
        junction_brush = QBrush(QColor(20, 20, 30))
        for (x, y), count in endpoint_counts.items():
            if count >= 3:
                r = 1.5
                dot = QGraphicsEllipseItem(x - r, y - r, r * 2, r * 2)
                dot.setPen(junction_pen)
                dot.setBrush(junction_brush)
                dot.setZValue(6)
                self._scene.addItem(dot)
                self._junction_items.append(dot)

    def _draw_overlay(self, overlay: EditorOverlayView) -> None:
        dash_pen = QPen(QColor(100, 140, 220))
        dash_pen.setStyle(Qt.PenStyle.DashLine)
        dash_pen.setWidthF(0.6)
        for segment in overlay.preview_wire_segments:
            line = QGraphicsLineItem(
                segment.x1_mm,
                segment.y1_mm,
                segment.x2_mm,
                segment.y2_mm,
            )
            line.setPen(dash_pen)
            line.setZValue(30)
            self._scene.addItem(line)
            self._overlay_items.append(line)
        if overlay.snap_x_mm is not None and overlay.snap_y_mm is not None:
            cx, cy = overlay.snap_x_mm, overlay.snap_y_mm
            size = 6.0
            for x1, y1, x2, y2 in (
                (cx - size, cy, cx + size, cy),
                (cx, cy - size, cx, cy + size),
            ):
                line = QGraphicsLineItem(x1, y1, x2, y2)
                cross_pen = QPen(QColor(180, 180, 200))
                cross_pen.setWidthF(0.3)
                line.setPen(cross_pen)
                line.setZValue(25)
                self._scene.addItem(line)
                self._overlay_items.append(line)

    def find_symbol_at(self, x_mm: float, y_mm: float) -> SymbolGraphicsItem | None:
        items = self._scene.items(QPointF(x_mm, y_mm))
        for item in items:
            if isinstance(item, SymbolGraphicsItem):
                return item
            parent = item.parentItem()
            while parent is not None:
                if isinstance(parent, SymbolGraphicsItem):
                    return parent
                parent = parent.parentItem()
        return None

    def find_wire_at(self, x_mm: float, y_mm: float) -> WireGraphicsItem | None:
        items = self._scene.items(QPointF(x_mm, y_mm))
        for item in items:
            if isinstance(item, WireGraphicsItem):
                return item
            parent = item.parentItem()
            if isinstance(parent, WireGraphicsItem):
                return parent
        return None

    def find_pin_at(self, x_mm: float, y_mm: float) -> UUID | None:
        for symbol in self._symbol_items:
            cp_id = symbol.pin_at_scene_pos(x_mm, y_mm)
            if cp_id is not None:
                return cp_id
        return None

    def set_tool_mode(self, mode: ToolMode) -> None:
        show_pins = mode == ToolMode.WIRE
        for symbol in self._symbol_items:
            symbol.set_pins_visible(show_pins)
